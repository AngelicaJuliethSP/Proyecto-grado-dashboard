"""
Parser de resultados de pruebas TestNG / Maven Surefire.

Convierte los archivos XML generados por Maven Surefire
(testng-results.xml y/o TEST-*.xml estilo JUnit) en un JSON
normalizado que alimenta el dashboard de indicadores.

Uso:
    python parser/results_parser.py --project SauceDemoAutomation \
        --reports-dir SauceDemoAutomation/target/surefire-reports \
        --output data/results.json
"""

import argparse
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

STATUS_MAP = {
    "PASS": "passed",
    "FAIL": "failed",
    "SKIP": "skipped",
}


def parse_testng_results(xml_path: Path) -> dict:
    """Parsea un archivo testng-results.xml de Surefire."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Surefire pone los totales como atributos del elemento raíz <testng-results>;
    # algunos formatos alternativos usan un hijo <summary>. Se soportan ambos.
    summary = root.find("summary")
    source = summary if summary is not None else root
    total = int(source.get("total", "0"))
    passed = int(source.get("passed", "0"))
    failures = int(source.get("failures", "0"))
    skipped = int(source.get("skipped", "0"))
    duration_ms = int(source.get("duration-ms", "0"))

    tests = []
    for method in root.iter("test-method"):
        raw_status = method.get("status", "SKIP").upper()
        status = STATUS_MAP.get(raw_status, "skipped")
        exception_type = None
        exception_msg = None

        exception = method.find("exception")
        if exception is not None:
            exception_type = exception.get("class")
            message = exception.find("message")
            exception_msg = message.text if message is not None else None

        tests.append({
            "name": method.get("name", "unknown"),
            "class": method.get("classname", "unknown"),
            "status": status,
            "duration_ms": int(method.get("duration-ms", "0")),
            "started_at": method.get("started-at"),
            "exception_type": exception_type,
            "exception_message": exception_msg,
        })

    return {
        "total": total,
        "passed": passed,
        "failed": failures,
        "skipped": skipped,
        "duration_ms": duration_ms,
        "tests": tests,
    }


def parse_junit_xml(xml_path: Path) -> dict:
    """Parsea un TEST-*.xml estilo JUnit (fallback si no hay testng-results.xml)."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    total = int(root.get("tests", "0"))
    failures = int(root.get("failures", "0"))
    errors = int(root.get("errors", "0"))
    skipped = int(root.get("skipped", "0"))
    duration_s = float(root.get("time", "0"))

    tests = []
    for case in root.iter("testcase"):
        status = "passed"
        exception_type = None
        exception_msg = None

        # Nota: no usar `find(...) or find(...)` — un elemento XML sin hijos
        # evalúa como False en Python y el fallo se perdería.
        failure = case.find("failure")
        if failure is None:
            failure = case.find("error")
        if failure is not None:
            status = "failed"
            exception_type = failure.get("type")
            exception_msg = failure.get("message")
        elif case.find("skipped") is not None:
            status = "skipped"

        tests.append({
            "name": case.get("name", "unknown"),
            "class": case.get("classname", "unknown"),
            "status": status,
            "duration_ms": int(float(case.get("time", "0")) * 1000),
            "started_at": None,
            "exception_type": exception_type,
            "exception_message": exception_msg,
        })

    return {
        "total": total,
        "passed": total - failures - errors - skipped,
        "failed": failures + errors,
        "skipped": skipped,
        "duration_ms": int(duration_s * 1000),
        "tests": tests,
    }


def parse_reports_dir(reports_dir: Path) -> dict:
    """Busca testng-results.xml o TEST-*.xml en el directorio de reportes."""
    testng_file = reports_dir / "testng-results.xml"
    if testng_file.exists():
        return parse_testng_results(testng_file)

    junit_files = sorted(reports_dir.glob("TEST-*.xml"))
    if junit_files:
        merged = {"total": 0, "passed": 0, "failed": 0, "skipped": 0,
                  "duration_ms": 0, "tests": []}
        for junit_file in junit_files:
            result = parse_junit_xml(junit_file)
            for key in ("total", "passed", "failed", "skipped", "duration_ms"):
                merged[key] += result[key]
            merged["tests"].extend(result["tests"])
        return merged

    raise FileNotFoundError(
        f"No se encontraron reportes (testng-results.xml o TEST-*.xml) en {reports_dir}"
    )


def build_record(project: str, reports_dir: Path, result: dict) -> dict:
    """Construye el registro normalizado de una ejecución."""
    now = datetime.now(timezone.utc)
    return {
        "project": project,
        "executed_at": now.isoformat(),
        "total": result["total"],
        "passed": result["passed"],
        "failed": result["failed"],
        "skipped": result["skipped"],
        "success_rate": round(result["passed"] / result["total"] * 100, 2) if result["total"] else 0.0,
        "duration_ms": result["duration_ms"],
        "tests": result["tests"],
    }


def append_to_store(store_path: Path, record: dict) -> None:
    """Agrega el registro al histórico JSON (data/results.json).

    Deduplica por (project, executed_at): si ya existe una ejecución con la
    misma clave, la reemplaza en lugar de duplicarla.
    """
    store_path.parent.mkdir(parents=True, exist_ok=True)
    if store_path.exists():
        with open(store_path, encoding="utf-8") as f:
            store = json.load(f)
    else:
        store = []

    key = (record["project"], record["executed_at"])
    store = [
        r for r in store
        if (r.get("project"), r.get("executed_at")) != key
    ]
    store.append(record)
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parser de resultados TestNG/Surefire")
    parser.add_argument("--project", required=True, help="Nombre del proyecto (ej. SauceDemoAutomation)")
    parser.add_argument("--reports-dir", required=True, help="Ruta a target/surefire-reports")
    parser.add_argument("--output", default="data/results.json", help="Archivo JSON del histórico")
    parser.add_argument("--executed-at", default=None,
                        help="Timestamp ISO de la ejecución (por defecto: ahora, UTC)")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    result = parse_reports_dir(reports_dir)
    record = build_record(args.project, reports_dir, result)
    if args.executed_at:
        record["executed_at"] = args.executed_at
    append_to_store(Path(args.output), record)

    print(f"[OK] {args.project}: {record['passed']}/{record['total']} passed "
          f"({record['success_rate']}%) -> {args.output}")


if __name__ == "__main__":
    main()

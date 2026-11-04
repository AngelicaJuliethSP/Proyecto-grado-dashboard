"""
Ingesta de resultados Allure (allure-results/*-result.json) para el dashboard.

Allure genera un archivo JSON por cada test ejecutado. Este módulo los
consolida en un registro normalizado compatible con data/results.json.

Uso:
    py parser/allure_ingest.py --project SauceDemoAutomation \
        --allure-dir <proyecto>/target/allure-results \
        --output data/results.json
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

STATUS_MAP = {
    "passed": "passed",
    "failed": "failed",
    "broken": "failed",
    "skipped": "skipped",
}


def load_allure_results(allure_dir: Path) -> pd.DataFrame:
    """Lee todos los *-result.json de un directorio allure-results en un DataFrame."""
    files = sorted(allure_dir.glob("*-result.json"))
    if not files:
        raise FileNotFoundError(f"No hay archivos *-result.json en {allure_dir}")

    frames = [pd.json_normalize(f.read_text(encoding="utf-8") and json.loads(f.read_text(encoding="utf-8"))) for f in files]
    df = pd.concat(frames, ignore_index=True)
    return df


def summarize(df: pd.DataFrame) -> dict:
    """Calcula los agregados de la ejecución a partir del DataFrame de resultados."""
    df = df.copy()
    df["status"] = df["status"].map(STATUS_MAP).fillna("skipped")
    df["duration_ms"] = (df["stop"] - df["start"]).fillna(0).astype("int64")

    total = len(df)
    passed = int((df["status"] == "passed").sum())
    failed = int((df["status"] == "failed").sum())
    skipped = int((df["status"] == "skipped").sum())

    tests = [
        {
            "name": row.get("name", "unknown"),
            "class": row.get("fullName", "unknown").rsplit(".", 1)[0] if pd.notna(row.get("fullName")) else "unknown",
            "status": row["status"],
            "duration_ms": int(row["duration_ms"]),
            "started_at": None,
            "exception_type": None,
            "exception_message": (row.get("statusDetails.message") if pd.notna(row.get("statusDetails.message")) else None),
        }
        for _, row in df.iterrows()
    ]

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "success_rate": round(passed / total * 100, 2) if total else 0.0,
        "duration_ms": int(df["duration_ms"].sum()),
        "tests": tests,
    }


def build_record(project: str, result: dict) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "project": project,
        "executed_at": now.isoformat(),
        **result,
    }


def append_to_store(store_path: Path, record: dict) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    if store_path.exists():
        with open(store_path, encoding="utf-8") as f:
            store = json.load(f)
    else:
        store = []
    store.append(record)
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta de resultados Allure para el dashboard")
    parser.add_argument("--project", required=True)
    parser.add_argument("--allure-dir", required=True, help="Ruta al directorio allure-results")
    parser.add_argument("--output", default="data/results.json")
    args = parser.parse_args()

    allure_dir = Path(args.allure_dir)
    df = load_allure_results(allure_dir)
    result = summarize(df)
    record = build_record(args.project, result)
    append_to_store(Path(args.output), record)

    print(f"[OK] {args.project}: {record['passed']}/{record['total']} passed "
          f"({record['success_rate']}%) desde Allure -> {args.output}")


if __name__ == "__main__":
    main()

"""
Ejecuta la línea base del proyecto de grado (Fase 0).

Corre cada suite N veces localmente, sin modificar código de pruebas,
limpiando allure-results/ antes de cada corrida para que los resultados
no se mezclen, e ingiere cada corrida al almacén del dashboard.

Uso:
    py scripts/run_baseline.py --runs 3
    py scripts/run_baseline.py --runs 3 --projects SauceDemoAutomation
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILOTO = ROOT / "piloto"
JAVA_HOME = r"C:/Users/angelica.silva01/.jdks/temurin-17.0.20.1"

ALL_PROJECTS = ["SauceDemoAutomation", "PetStoreRestAssured", "WdioMobileAutomation"]


def run_mvn_tests(project_dir: Path) -> tuple[bool, str]:
    """Ejecuta mvn clean test y retorna (exit_ok, salida_relevante)."""
    env = {
        **subprocess.os.environ,
        "JAVA_HOME": JAVA_HOME,
        "PATH": f"{JAVA_HOME}/bin;{subprocess.os.environ.get('PATH', '')}",
    }
    proc = subprocess.run(
        ["mvn.cmd", "clean", "test", "-B"],
        cwd=project_dir,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )
    relevant = "\n".join(
        line for line in proc.stdout.splitlines()
        if "Tests run" in line or "BUILD" in line
    )
    return proc.returncode == 0, relevant


def ingest_run(project: str, project_dir: Path, output: Path) -> None:
    """Ingiere la última corrida. Prefiere Allure JSON; respaldo: surefire XML."""
    allure_dir = project_dir / "allure-results"
    try:
        subprocess.run(
            [
                sys.executable, str(ROOT / "parser" / "allure_ingest.py"),
                "--project", project,
                "--allure-dir", str(allure_dir),
                "--output", str(output),
            ],
            cwd=ROOT, check=True,
        )
    except subprocess.CalledProcessError:
        subprocess.run(
            [
                sys.executable, str(ROOT / "parser" / "results_parser.py"),
                "--project", project,
                "--reports-dir", str(project_dir / "target" / "surefire-reports"),
                "--output", str(output),
            ],
            cwd=ROOT, check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Línea base del proyecto de grado")
    parser.add_argument("--runs", type=int, default=3, help="Corridas por proyecto")
    parser.add_argument("--projects", nargs="+", default=ALL_PROJECTS, choices=ALL_PROJECTS)
    parser.add_argument("--output", default="data/results.json")
    args = parser.parse_args()

    output = ROOT / args.output
    summary = []

    for project in args.projects:
        project_dir = PILOTO / project
        allure_dir = project_dir / "allure-results"
        print(f"\n=== {project} — {args.runs} corridas ===")
        for run in range(1, args.runs + 1):
            # limpiar resultados acumulados para que cada corrida sea independiente
            if allure_dir.exists():
                shutil.rmtree(allure_dir)

            print(f"[{project}] corrida {run}/{args.runs}...")
            ok, mvn_output = run_mvn_tests(project_dir)
            last_line = mvn_output.strip().splitlines()[-1] if mvn_output.strip() else "(sin salida)"
            print(f"  mvn: {'OK' if ok else 'FALLO'} | {last_line}")

            ingest_run(project, project_dir, output)
            print(f"  [OK] corrida {run} ingerida")

    # resumen final
    with open(output, encoding="utf-8") as f:
        store = json.load(f)
    print(f"\n=== Resumen ({len(store)} ejecuciones registradas) ===")
    for record in store:
        print(
            f"  {record['project']:<22} {record['passed']}/{record['total']} "
            f"({record['success_rate']}%) @ {record['executed_at'][:19]}"
        )


if __name__ == "__main__":
    main()

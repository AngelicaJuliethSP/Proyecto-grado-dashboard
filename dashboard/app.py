"""
Dashboard de visualización y análisis de reportes de ejecución
de pruebas automatizadas.

Proyecto de grado — indicadores de calidad y estabilidad del
proceso de automatización integrado a un pipeline de CI.

Ejecutar con:
    streamlit run dashboard/app.py
"""

import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "results.json"

st.set_page_config(
    page_title="Dashboard QA — Proyecto de Grado",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Dashboard de Ejecución de Pruebas Automatizadas")
st.caption("Indicadores de calidad y estabilidad del proceso de automatización — integrado a CI")


@st.cache_data(ttl=30)
def load_data() -> pd.DataFrame:
    """Carga el histórico de ejecuciones desde data/results.json."""
    if not DATA_PATH.exists():
        return pd.DataFrame()
    with open(DATA_PATH, encoding="utf-8") as f:
        records = json.load(f)
    if not records:
        return pd.DataFrame()
    df = pd.json_normalize(records)
    df["executed_at"] = pd.to_datetime(df["executed_at"])
    return df.sort_values("executed_at")


def main() -> None:
    df = load_data()

    if df.empty:
        st.warning(
            "⚠️ Aún no hay resultados. Ejecuta el pipeline de CI o el parser manualmente:\n\n"
            "```\n"
            "python parser/results_parser.py --project <nombre> --reports-dir <ruta>/surefire-reports\n"
            "```"
        )
        st.stop()

    # ---- Filtros ----
    with st.sidebar:
        st.header("🔎 Filtros")
        projects = ["Todos"] + sorted(df["project"].unique().tolist())
        selected_project = st.selectbox("Proyecto", projects)
        if selected_project != "Todos":
            df = df[df["project"] == selected_project]

    # ---- KPIs globales ----
    last_run = df.iloc[-1]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Ejecuciones registradas", len(df))
    col2.metric("Última tasa de éxito", f"{last_run['success_rate']}%")
    col3.metric("Tests (última ejecución)", int(last_run["total"]))
    col4.metric("Fallos (última ejecución)", int(last_run["failed"]))
    col5.metric("Duración (última ejec.)", f"{last_run['duration_ms'] / 1000:.1f}s")

    st.divider()

    # ---- Tendencia histórica ----
    st.subheader("📈 Tendencia de tasa de éxito por ejecución")
    trend = df[["executed_at", "project", "success_rate"]].copy()
    trend_pivot = trend.pivot_table(index="executed_at", columns="project",
                                    values="success_rate", aggfunc="last")
    st.line_chart(trend_pivot)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🧪 Resultados por ejecución")
        stacked = df[["executed_at", "project", "passed", "failed", "skipped"]].copy()
        stacked = stacked.set_index("executed_at")[["passed", "failed", "skipped"]]
        st.bar_chart(stacked)

    with col_right:
        st.subheader("⏱️ Duración de ejecuciones (segundos)")
        duration = df.set_index("executed_at")["duration_ms"] / 1000
        st.bar_chart(duration)

    st.divider()

    # ---- Tests más fallidos ----
    st.subheader("🔥 Tests más fallidos (histórico)")
    if "tests" in df.columns:
        test_rows = df.explode("tests").dropna(subset=["tests"])
        if not test_rows.empty:
            tests_df = pd.json_normalize(test_rows["tests"])
            tests_df["project"] = test_rows["project"].values
            failed_tests = tests_df[tests_df["status"] == "failed"]
            if not failed_tests.empty:
                top_failed = (
                    failed_tests.groupby(["project", "class", "name"])
                    .size()
                    .reset_index(name="fallos")
                    .sort_values("fallos", ascending=False)
                    .head(10)
                )
                st.dataframe(top_failed, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No hay tests fallidos en el histórico registrado.")
        else:
            st.info("Sin detalle de tests disponible.")

    # ---- Tabla de ejecuciones ----
    st.subheader("📋 Histórico de ejecuciones")
    table = df[["executed_at", "project", "total", "passed", "failed",
                "skipped", "success_rate", "duration_ms"]].copy()
    table["executed_at"] = table["executed_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
    table["duration_ms"] = (table["duration_ms"] / 1000).round(1)
    table = table.rename(columns={
        "executed_at": "Fecha", "project": "Proyecto", "total": "Total",
        "passed": "Pasados", "failed": "Fallidos", "skipped": "Omitidos",
        "success_rate": "Éxito %", "duration_ms": "Duración (s)",
    })
    st.dataframe(table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

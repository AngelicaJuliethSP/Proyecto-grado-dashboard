"""
Dashboard de visualización y análisis de reportes de ejecución
de pruebas automatizadas.

Proyecto de grado — indicadores de calidad y estabilidad del
proceso de automatización integrado a un pipeline de CI.

Ejecutar con:
    streamlit run dashboard/app.py
"""

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "results.json"

# ---- Estilos personalizados ----
CUSTOM_CSS = """
<style>
    /* Encabezado principal */
    .hero-header {
        background: linear-gradient(135deg, #1f3b73 0%, #2d5ba8 60%, #3f7ad1 100%);
        border-radius: 14px;
        padding: 1.6rem 2rem;
        margin-bottom: 1.2rem;
    }
    .hero-header h1 {
        color: #ffffff;
        font-size: 1.9rem;
        margin: 0 0 0.4rem 0;
    }
    .hero-header p {
        color: #dce7f7;
        font-size: 1rem;
        margin: 0;
    }
    /* Tarjetas de objetivos */
    .obj-card {
        background: #f4f7fc;
        border-left: 4px solid #2d5ba8;
        border-radius: 8px;
        padding: 0.8rem 1.1rem;
        margin-bottom: 0.6rem;
    }
    .obj-card b { color: #1f3b73; }
    /* Pie de página */
    .app-footer {
        text-align: center;
        color: #8a94a6;
        font-size: 0.85rem;
        padding: 1.2rem 0 0.5rem 0;
        border-top: 1px solid #e6eaf0;
        margin-top: 2rem;
    }
    /* Métricas con fondo suave */
    div[data-testid="stMetric"] {
        background: #f8fafd;
        border: 1px solid #e6eaf0;
        border-radius: 10px;
        padding: 0.9rem 1rem;
    }
</style>
"""

st.set_page_config(
    page_title="Dashboard QA — Proyecto de Grado",
    page_icon="📊",
    layout="wide",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-header">
        <h1>📊 Dashboard de Ejecución de Pruebas Automatizadas</h1>
        <p>Indicadores de calidad y estabilidad del proceso de automatización — integrado a un pipeline de CI</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("🎯 Objetivos del proyecto", expanded=False):
    st.markdown(
        """
        <div class="obj-card"><b>Objetivo general:</b> implementar un dashboard para la
        visualización y análisis de reportes de ejecución de pruebas automatizadas,
        integrado a un pipeline de integración continua, con el propósito de centralizar
        los resultados y facilitar el seguimiento de indicadores de calidad y estabilidad
        del proceso de automatización.</div>
        <div class="obj-card"><b>Objetivo específico 1:</b> consolidar y refactorizar los
        frameworks de automatización desarrollados para aplicaciones móviles (Appium),
        web (Selenium) y servicios REST (REST Assured), aplicando buenas prácticas de
        diseño, organización y mantenibilidad.</div>
        <div class="obj-card"><b>Objetivo específico 2:</b> integrar los frameworks a un
        pipeline de integración continua, de modo que las suites se ejecuten
        automáticamente ante cambios en el código fuente.</div>
        <div class="obj-card"><b>Objetivo específico 3:</b> implementar un mecanismo de
        generación y consolidación de reportes con resultados de éxito y fallo, tiempos
        de ejecución y comportamiento de las pruebas.</div>
        <div class="obj-card"><b>Objetivo específico 4:</b> desarrollar un dashboard que
        muestre resultados históricos mediante indicadores y tendencias, e identifique
        variaciones de calidad y pruebas inestables.</div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Documento 7.2 — Proyecto de grado. Suites: SauceDemo (Web/Selenium) · PetStore (API/REST Assured) · WdioMobile (Mobile/Appium).")


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
    # format="mixed": el almacén combina timestamps con/sin microsegundos y
    # con distintas zonas horarias (+00:00, -05:00); sin esto pandas infiere
    # el formato del primer registro y falla con los demás.
    df["executed_at"] = pd.to_datetime(df["executed_at"], format="mixed", utc=True)
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

    st.divider()

    # ---- Comparativa entre suites ----
    st.subheader("⚖️ Comparativa entre suites")
    by_suite = df.groupby("project").agg(
        ejecuciones=("executed_at", "count"),
        tests=("total", "sum"),
        pasados=("passed", "sum"),
        fallidos=("failed", "sum"),
        omitidos=("skipped", "sum"),
        exito_prom=("success_rate", "mean"),
        duracion_prom=("duration_ms", "mean"),
    ).round({"exito_prom": 1, "duracion_prom": 0})
    by_suite["duracion_prom"] = (by_suite["duracion_prom"] / 1000).round(1)

    col_comp_chart, col_comp_table = st.columns(2)
    with col_comp_chart:
        st.caption("% de éxito promedio por suite")
        st.bar_chart(by_suite["exito_prom"])
    with col_comp_table:
        st.caption("Resumen agregado por suite")
        st.dataframe(
            by_suite.rename(columns={
                "exito_prom": "Éxito % prom.",
                "duracion_prom": "Duración prom. (s)",
            }),
            width="stretch",
        )

    st.divider()

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
                st.dataframe(top_failed, width="stretch", hide_index=True)
            else:
                st.success("✅ No hay tests fallidos en el histórico registrado.")
        else:
            st.info("Sin detalle de tests disponible.")

    # ---- Matriz de causa raíz probable ----
    st.subheader("🧩 Matriz de causa raíz probable")
    st.caption("Clasificación automática de los fallos recurrentes según el mensaje de error (análisis por patrones).")

    CAUSE_PATTERNS = [
        ("⏱️ Timeouts / Asincronía", [
            r"timeout", r"timed?\s*out", r"time\s*elapsed.*<<<", r"timeoutexception",
            r"expected condition failed", r"waiting for", r"anr",
        ]),
        ("🔀 Concurrencia / Condiciones de carrera", [
            r"stale\s*element", r"element\s*not\s*interactable", r"race\s*condition",
            r"concurrent", r"detached",
        ]),
        ("🌐 Dependencias externas / Fallos de red", [
            r"connection\s*refused", r"connection\s*reset", r"unknownhost", r"dns",
            r"socket", r"network", r"502", r"503", r"504", r"could\s*not\s*connect",
        ]),
        ("🗃️ Datos de prueba / Falta de aislamiento", [
            r"duplicate", r"already\s*exists", r"conflict", r"409",
            r"assert.*equal.*expected", r"element\s*could\s*not\s*be\s*located",
        ]),
        ("🔍 Fallo de aserción (comportamiento)", [
            r"expected\s*\[", r"but\s*found", r"assertion", r"no\s*visible",
        ]),
        ("🖥️ Infraestructura / Entorno de ejecución", [
            r"session\s*not\s*created", r"could\s*not\s*start\s*a\s*new\s*session",
            r"webview", r"renderiz", r"swiftshader", r"emulator", r"device",
            r"systemui", r"crash", r"no\s*such\s*element",
        ]),
    ]

    def classify_cause(message: str) -> str:
        text = (message or "").lower()
        for cause, patterns in CAUSE_PATTERNS:
            if any(re.search(p, text) for p in patterns):
                return cause
        return "❓ Sin clasificar"

    if "tests" in df.columns:
        test_rows = df.explode("tests").dropna(subset=["tests"])
        if not test_rows.empty:
            tests_df = pd.json_normalize(test_rows["tests"])
            tests_df["project"] = test_rows["project"].values
            failed_tests = tests_df[tests_df["status"] == "failed"].copy()
            if not failed_tests.empty:
                failed_tests["causa"] = failed_tests["exception_message"].apply(classify_cause)
                cause_matrix = (
                    failed_tests.groupby(["project", "causa"])
                    .size().reset_index(name="fallos")
                    .sort_values(["project", "fallos"], ascending=[True, False])
                )
                st.dataframe(cause_matrix, width="stretch", hide_index=True)
            else:
                st.success("✅ No hay fallos que clasificar en el histórico registrado.")
        else:
            st.info("Sin detalle de tests disponible.")
    else:
        st.info("Sin detalle de tests disponible.")

    # ---- Top bottlenecks ----
    st.subheader("🐢 Top bottlenecks (pruebas más lentas)")
    st.caption("Ranking de tests que más tiempo consumen en el histórico — candidatos a optimización (Principio de Pareto).")
    if "tests" in df.columns:
        test_rows = df.explode("tests").dropna(subset=["tests"])
        if not test_rows.empty:
            tests_df = pd.json_normalize(test_rows["tests"])
            tests_df["project"] = test_rows["project"].values
            slowest = (
                tests_df.groupby(["project", "class", "name"])["duration_ms"]
                .agg(total_ms="sum", ejecuciones="count", prom_ms="mean")
                .reset_index()
                .sort_values("total_ms", ascending=False)
                .head(10)
            )
            total_all = tests_df["duration_ms"].sum()
            if total_all > 0:
                slowest["% del tiempo total"] = (slowest["total_ms"] / total_all * 100).round(1)
            slowest["total_s"] = (slowest["total_ms"] / 1000).round(1)
            slowest["prom_s"] = (slowest["prom_ms"] / 1000).round(2)
            st.dataframe(
                slowest[["project", "class", "name", "ejecuciones",
                         "total_s", "prom_s", "% del tiempo total"]],
                width="stretch", hide_index=True,
            )
        else:
            st.info("Sin detalle de tests disponible.")
    else:
        st.info("Sin detalle de tests disponible.")

    # ---- Pruebas inestables (flaky) ----
    st.subheader("🎲 Pruebas inestables (flaky)")
    st.caption("Tests que han alternado entre éxito y fallo entre ejecuciones — señal de inestabilidad del entorno o del test.")
    if "tests" in df.columns:
        test_rows = df.explode("tests").dropna(subset=["tests"])
        if not test_rows.empty:
            tests_df = pd.json_normalize(test_rows["tests"])
            tests_df["project"] = test_rows["project"].values
            status_per_test = (
                tests_df.groupby(["project", "class", "name"])["status"]
                .agg(lambda s: set(s.dropna()))
                .reset_index()
            )
            flaky = status_per_test[
                status_per_test["status"].apply(
                    lambda statuses: "passed" in statuses and "failed" in statuses
                )
            ].drop(columns=["status"])
            if not flaky.empty:
                flaky = flaky.assign(inestable="⚠️ Alterna éxito/fallo")
                st.dataframe(flaky, width="stretch", hide_index=True)
            else:
                st.success("✅ No se detectaron pruebas inestables en el histórico registrado.")
        else:
            st.info("Sin detalle de tests disponible.")
    else:
        st.info("Sin detalle de tests disponible.")

    # ---- Detalle por test ----
    st.subheader("🔬 Detalle por test")
    if "tests" in df.columns:
        test_rows = df.explode("tests").dropna(subset=["tests"])
        if not test_rows.empty:
            tests_df = pd.json_normalize(test_rows["tests"])
            tests_df["project"] = test_rows["project"].values
            tests_df["executed_at"] = test_rows["executed_at"].values

            col_status, col_search, col_project = st.columns([1, 2, 1])
            with col_status:
                status_filter = st.selectbox(
                    "Estado", ["Todos", "passed", "failed", "skipped"])
            with col_search:
                search = st.text_input("Buscar (nombre o clase)")
            with col_project:
                proj_options = ["Todos"] + sorted(tests_df["project"].unique().tolist())
                proj_filter = st.selectbox("Suite", proj_options)

            filtered = tests_df
            if status_filter != "Todos":
                filtered = filtered[filtered["status"] == status_filter]
            if search:
                mask = (
                    filtered["name"].str.contains(search, case=False, na=False)
                    | filtered["class"].str.contains(search, case=False, na=False)
                )
                filtered = filtered[mask]
            if proj_filter != "Todos":
                filtered = filtered[filtered["project"] == proj_filter]

            detail = filtered[["executed_at", "project", "class", "name",
                               "status", "duration_ms"]].copy()
            detail["executed_at"] = detail["executed_at"].dt.strftime("%Y-%m-%d %H:%M")
            detail["duration_ms"] = (detail["duration_ms"] / 1000).round(2)
            detail = detail.rename(columns={
                "executed_at": "Fecha", "project": "Suite", "class": "Clase",
                "name": "Test", "status": "Estado", "duration_ms": "Duración (s)",
            })
            st.dataframe(detail, width="stretch", hide_index=True,
                         height=320)
        else:
            st.info("Sin detalle de tests disponible.")
    else:
        st.info("Sin detalle de tests disponible.")

    st.divider()

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
    st.dataframe(table, width="stretch", hide_index=True)

    st.markdown(
        """
        <div class="app-footer">
            Dashboard QA — Proyecto de grado · Suites: SauceDemo (Web) · PetStore (API) · WdioMobile (Mobile) ·
            Datos: <code>data/results.json</code>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

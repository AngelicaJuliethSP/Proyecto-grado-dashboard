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
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "results.json"

# ---- Metas de calidad por suite (acordadas con el equipo) ----
# fallos_max: fallos permitidos por ejecución
# exito_min: tasa de éxito mínima (%)
# duracion_suite_max_s: duración máxima de la suite (segundos)
# duracion_test_max_s: duración máxima por test individual (segundos)
# flaky_max: máximo de pruebas inestables permitidas
GOALS = {
    "PetStoreRestAssured": {
        "label": "PetStore (API)",
        "fallos_max": 0,
        "exito_min": 100.0,
        "duracion_suite_max_s": 10,
        "duracion_test_max_s": 5,
        "flaky_max": 0,
    },
    "SauceDemoAutomation": {
        "label": "SauceDemo (Web)",
        "fallos_max": 0,
        "exito_min": 100.0,
        "duracion_suite_max_s": 30,
        "duracion_test_max_s": 10,
        "flaky_max": 0,
    },
    "WdioMobileAutomation": {
        "label": "WdioMobile (Mobile)",
        "fallos_max": 1,
        "exito_min": 90.0,
        "duracion_suite_max_s": 240,
        "duracion_test_max_s": 30,
        "flaky_max": 0,
    },
}
DEFAULT_GOAL = {"label": "", "fallos_max": 0, "exito_min": 100.0,
                "duracion_suite_max_s": 60, "duracion_test_max_s": 15,
                "flaky_max": 0}

COLOR_OK = "#1a7f37"      # verde: cumple la meta
COLOR_BAD = "#c62828"     # rojo: no cumple la meta
COLOR_WARN = "#e6a700"    # amarillo: advertencia (duración por test)

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


def goal_for(project: str) -> dict:
    """Devuelve la meta de una suite, o valores por defecto si no está definida."""
    return GOALS.get(project, DEFAULT_GOAL)


def _badge(text: str, color: str) -> str:
    """Chip HTML con fondo de color para señalar cumplimiento de metas."""
    return (f'<span style="background:{color};color:#fff;border-radius:12px;'
            f'padding:2px 10px;font-size:0.85rem;font-weight:600;">{text}</span>')


def eval_metric(cumple: bool, ok_text: str, bad_text: str) -> str:
    """HTML de badge verde/rojo según cumpla la meta."""
    return _badge(ok_text if cumple else bad_text,
                  COLOR_OK if cumple else COLOR_BAD)


def metric_html(value: str, cumple: bool, meta_text: str) -> str:
    """Tarjeta de métrica con borde verde/rojo según la meta."""
    color = COLOR_OK if cumple else COLOR_BAD
    estado = "✔ cumple" if cumple else "✘ no cumple"
    return (f'<div style="background:#f8fafd;border:1.5px solid {color};'
            f'border-radius:10px;padding:0.9rem 1rem;">'
            f'<div style="font-size:0.85rem;color:#57606a;margin-bottom:0.2rem;">{meta_text}</div>'
            f'<div style="font-size:1.6rem;font-weight:700;color:{color};">{value}</div>'
            f'<div style="font-size:0.8rem;color:{color};margin-top:0.2rem;">{estado}</div>'
            f'</div>')


def flaky_count(df: pd.DataFrame, project: str) -> int:
    """Número de pruebas inestables (alternan éxito/fallo) de una suite."""
    sub = df[df["project"] == project]
    if "tests" not in sub.columns or sub.empty:
        return 0
    rows = sub.explode("tests").dropna(subset=["tests"])
    if rows.empty:
        return 0
    tdf = pd.json_normalize(rows["tests"])
    statuses = tdf.groupby(["class", "name"])["status"].agg(
        lambda s: set(s.dropna()))
    return int(statuses.apply(
        lambda st_: "passed" in st_ and "failed" in st_).sum())


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
    # Con filtro "Todos", la última ejecución de CADA proyecto se consolida
    # en un valor global (antes: df.iloc[-1] tomaba la última fila de un
    # solo proyecto arbitrario y presentaba ese valor como global).
    last_per_project = df.groupby("project").last().reset_index()
    global_passed = int(last_per_project["passed"].sum())
    global_total = int(last_per_project["total"].sum())
    global_failed = int(last_per_project["failed"].sum())
    global_rate = round(global_passed / global_total * 100, 1) if global_total else 0.0
    last_ts = df["executed_at"].max().strftime("%d-%b %H:%M UTC")

    # Evaluación contra metas: la peor suite define el estado global
    # (si una suite no cumple, el consolidado global se marca en rojo).
    goals = {p: goal_for(p) for p in last_per_project["project"]}
    cumple_global = all(
        int(row["failed"]) <= goals[p]["fallos_max"]
        and float(row["success_rate"]) >= goals[p]["exito_min"]
        and row["duration_ms"] / 1000 <= goals[p]["duracion_suite_max_s"]
        for p, row in last_per_project.set_index("project").iterrows()
    )
    cumple_flaky_global = all(
        flaky_count(df, p) <= goals[p]["flaky_max"] for p in last_per_project["project"]
    )

    st.subheader("🎯 Estado global vs metas de calidad")
    with st.expander("📋 Ver metas definidas por suite", expanded=False):
        goals_rows = []
        for p, g in GOALS.items():
            goals_rows.append({
                "Suite": g["label"],
                "Fallos máx./ejecución": g["fallos_max"],
                "Éxito mínimo (%)": g["exito_min"],
                "Duración máx. suite (s)": g["duracion_suite_max_s"],
                "Duración máx. test (s)": g["duracion_test_max_s"],
                "Flaky máx.": g["flaky_max"],
            })
        st.dataframe(pd.DataFrame(goals_rows), width="stretch", hide_index=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(metric_html(str(len(df)), True, "Ejecuciones registradas"), unsafe_allow_html=True)
    with col2:
        st.markdown(metric_html(f"{global_rate}%", cumple_global, "Última tasa de éxito (global)"), unsafe_allow_html=True)
    with col3:
        st.markdown(metric_html(str(global_total), True, "Tests (última ejec. por suite)"), unsafe_allow_html=True)
    with col4:
        st.markdown(metric_html(str(global_failed), global_failed == 0, "Fallos (última ejec. por suite)"), unsafe_allow_html=True)
    with col5:
        dur_total = last_per_project["duration_ms"].sum() / 1000
        st.markdown(metric_html(f"{dur_total:.1f}s", cumple_global, "Duración (última ejec. por suite)"), unsafe_allow_html=True)
    if not cumple_global:
        st.error("⚠️ La última ejecución de una o más suites no cumple las metas de calidad definidas (fallos, éxito o duración).")
    if not cumple_flaky_global:
        st.error("⚠️ Una o más suites superan el máximo de pruebas inestables (flaky) permitido.")

    st.divider()

    # ---- Tendencia histórica ----
    st.subheader("📈 Tendencia de tasa de éxito por ejecución")
    st.caption("Eje X = número de ejecución de cada suite (de la más antigua a la más reciente). "
               "Pasa el cursor sobre cada punto para ver la fecha exacta. "
               "Línea punteada = meta de éxito de cada suite.")
    trend = df[["executed_at", "project", "success_rate"]].copy().sort_values("executed_at")
    trend["ejecucion_n"] = trend.groupby("project").cumcount() + 1
    trend["suite"] = trend["project"].map(lambda p: goal_for(p)["label"])
    trend["fecha"] = trend["executed_at"].dt.strftime("%d-%b %H:%M")
    fig_trend = px.line(
        trend, x="ejecucion_n", y="success_rate", color="suite",
        markers=True,
        hover_data={
            "fecha": True, "success_rate": ":.1f",
            "ejecucion_n": False, "suite": False,
        },
    )
    # Una línea de meta por suite (100/90/80%): quedan bien separadas en el eje
    for project in sorted(trend["project"].unique()):
        meta = goal_for(project)["exito_min"]
        fig_trend.add_hline(y=meta, line_dash="dot", line_color="#1f3b73",
                            annotation_text=f"meta {goal_for(project)['label']}: {meta}%",
                            annotation_position="right")
    fig_trend.update_layout(
        height=380, xaxis_title="Número de ejecución", yaxis_title="Éxito %",
        yaxis_range=[0, 108],
        legend=dict(orientation="h", y=-0.3),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_trend, width="stretch")

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

    # Badges "Estado" y "Fallos vs meta" eliminados: no aportaban información
    # (redundantes con la gráfica) y el HTML no se renderiza en st.dataframe.
    # El cumplimiento se lee directamente en la gráfica (verde/rojo) y en las
    # columnas numéricas "Éxito % prom." y "Duración prom. (s)".


    col_comp_chart, col_comp_table = st.columns(2)
    with col_comp_chart:
        st.caption("% de éxito promedio por suite (verde = cumple meta, rojo = no cumple)")
        by_suite["cumple_meta"] = by_suite.index.map(lambda p: (
            int(by_suite.loc[p, "fallidos"]) <= goal_for(p)["fallos_max"]
            and float(by_suite.loc[p, "exito_prom"]) >= goal_for(p)["exito_min"]
            and float(by_suite.loc[p, "duracion_prom"]) <= goal_for(p)["duracion_suite_max_s"]
        ))
        fig_comp = px.bar(
            by_suite.reset_index(), x="project", y="exito_prom",
            color="cumple_meta",
            color_discrete_map={True: COLOR_OK, False: COLOR_BAD},
        )
        for p in by_suite.index:
            meta = goal_for(p)["exito_min"]
            fig_comp.add_hline(
                y=meta, line_dash="dot", line_color="#1f3b73",
                annotation_text=f"meta {goal_for(p)['label']}: {meta}%",
                annotation_position="top left",
            )
        fig_comp.update_layout(
            xaxis_title="", yaxis_title="Éxito % prom.",
            showlegend=False, height=380,
        )
        st.plotly_chart(fig_comp, width="stretch")
    with col_comp_table:
        st.caption("Resumen agregado por suite")
        st.dataframe(
            by_suite.drop(columns=["cumple_meta"]).rename(columns={
                "exito_prom": "Éxito % prom.",
                "duracion_prom": "Duración prom. (s)",
            }),
            width="stretch",
        )

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🧪 Resultados por ejecución")
        st.caption("Cada punto = una ejecución. Verde = tests pasados, rojo = fallidos, gris = omitidos. Usa el selector para enfocarte en una suite.")
        # Selector de suite para no mezclar ejecuciones de proyectos distintos
        # en un mismo eje (antes: 12 series apiladas ilegibles).
        suite_options = ["Todas"] + sorted(df["project"].unique().tolist())
        suite_sel = st.selectbox("Suite a visualizar", suite_options, key="stacked_suite")
        stacked_df = df if suite_sel == "Todas" else df[df["project"] == suite_sel]
        stacked_df = stacked_df.sort_values("executed_at").reset_index(drop=True)
        stacked_df["etiqueta"] = stacked_df["executed_at"].dt.strftime("%d-%b %H:%M")
        fig_stack = go.Figure()
        fig_stack.add_bar(
            x=stacked_df["etiqueta"], y=stacked_df["passed"],
            name="Pasados", marker_color="#1a7f37",
            customdata=stacked_df["project"],
            hovertemplate="%{customdata}<br>%{x}<br>Pasados: %{y}<extra></extra>",
        )
        fig_stack.add_bar(
            x=stacked_df["etiqueta"], y=stacked_df["failed"],
            name="Fallidos", marker_color="#c62828",
            customdata=stacked_df["project"],
            hovertemplate="%{customdata}<br>%{x}<br>Fallidos: %{y}<extra></extra>",
        )
        fig_stack.add_bar(
            x=stacked_df["etiqueta"], y=stacked_df["skipped"],
            name="Omitidos", marker_color="#9aa4b2",
            customdata=stacked_df["project"],
            hovertemplate="%{customdata}<br>%{x}<br>Omitidos: %{y}<extra></extra>",
        )
        fig_stack.update_layout(
            barmode="stack", height=380,
            xaxis_title="", yaxis_title="Tests",
            legend=dict(orientation="h", y=-0.25),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_stack, width="stretch")

    with col_right:
        st.subheader("⏱️ Duración de ejecuciones (segundos)")
        st.caption("Cada suite tiene su propio color. "
                   "Borde rojo = esa ejecución tardó más de lo esperado (meta en el hover). "
                   "Escala logarítmica para que las suites rápidas (API ~3s) no queden invisibles junto a la móvil (~200s).")
        duration = df[["executed_at", "project", "duration_ms"]].copy()
        duration["duracion_s"] = duration["duration_ms"] / 1000
        duration["cumple"] = duration.apply(
            lambda r: r["duracion_s"] <= goal_for(r["project"])["duracion_suite_max_s"], axis=1)
        duration["suite"] = duration["project"].map(lambda p: goal_for(p)["label"])
        duration["estado"] = duration["cumple"].map(
            {True: "✔ dentro de la meta", False: "✘ tardó más de lo esperado"})
        duration["ejecucion_n"] = duration.groupby("project").cumcount() + 1
        # Un color distintivo por suite para identificarlas de un vistazo
        SUITE_COLORS = {
            "PetStore (API)": "#1f77b4",     # azul
            "SauceDemo (Web)": "#ff7f0e",    # naranja
            "WdioMobile (Mobile)": "#9467bd",  # morado
        }
        fig_dur = px.bar(
            duration, x="ejecucion_n", y="duracion_s", color="suite",
            color_discrete_map=SUITE_COLORS,
            custom_data=["suite", "estado"],
        )
        # Borde rojo en las barras que exceden la meta (la barra conserva
        # el color de su suite; el incumplimiento no pasa desapercibido)
        label_to_project = {g["label"]: p for p, g in GOALS.items()}
        for trace in fig_dur.data:
            project = label_to_project.get(trace.name, trace.name)
            meta = goal_for(project)["duracion_suite_max_s"]
            cumple_trace = duration[duration["project"] == project]["cumple"].tolist()
            trace.marker.line = dict(
                width=2,
                color=[COLOR_BAD if not c else "rgba(0,0,0,0)" for c in cumple_trace],
            )
            trace.name = f"{goal_for(project)['label']} (meta ≤{meta}s)"
            trace.hovertemplate = (
                "%{customdata[0]}<br>Ejecución %{x}<br>Duración: %{y:.1f}s<br>"
                "%{customdata[1]}<extra></extra>")
        # Línea de meta por suite (solo si hay una suite en el filtro)
        if df["project"].nunique() == 1:
            meta_suite = goal_for(df["project"].iloc[0])["duracion_suite_max_s"]
            fig_dur.add_hline(y=meta_suite, line_dash="dot", line_color="#1f3b73",
                              annotation_text=f"meta: {meta_suite}s")
        fig_dur.update_layout(
            barmode="group", height=380,
            xaxis_title="Número de ejecución", yaxis_title="Duración (s)",
            yaxis_type="log",
            legend=dict(orientation="h", y=-0.25),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_dur, width="stretch")
        # Alerta de duración por test individual
        if "tests" in df.columns:
            rows = df.explode("tests").dropna(subset=["tests"])
            if not rows.empty:
                tdf = pd.json_normalize(rows["tests"])
                tdf["project"] = rows["project"].values
                tdf["duracion_s"] = tdf["duration_ms"] / 1000
                lentos = tdf[tdf.apply(
                    lambda r: r["duracion_s"] > goal_for(r["project"])["duracion_test_max_s"],
                    axis=1)]
                if not lentos.empty:
                    resumen = (lentos.groupby("project")
                               .agg(tests_lentos=("name", "count"),
                                    peor=("duracion_s", "max"))
                               .reset_index())
                    for _, r in resumen.iterrows():
                        st.warning(
                            f"⏱️ **{goal_for(r['project'])['label']}**: {r['tests_lentos']} tests tardaron más de "
                            f"{goal_for(r['project'])['duracion_test_max_s']}s (el más lento: {r['peor']:.1f}s). "
                            f"Revisa la sección 'Top bottlenecks'.")

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

    # Nota de orden: "Infraestructura" se evalúa ANTES que "Timeouts" porque
    # fallos de sesión (Could not start a new session... adbExec timeout) y
    # NoSuchElement (Command duration or timeout) contienen la palabra
    # "timeout" en el mensaje de Selenium sin ser timeouts reales.
    CAUSE_PATTERNS = [
        ("🖥️ Infraestructura / Entorno de ejecución", [
            r"session\s*not\s*created", r"could\s*not\s*start\s*a\s*new\s*session",
            r"webview", r"renderiz", r"swiftshader", r"emulator", r"device",
            r"systemui", r"crash", r"no\s*such\s*element", r"adbexec",
            r"could\s*not\s*start\s*a\s*new\s*session", r"response\s*code\s*500",
        ]),
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
    ]
    def _texto(valor) -> str:
        # pandas representa los campos vacíos como NaN (float), no como None;
        # "NaN or ''" devuelve NaN y .lower() falla. Se normaliza a texto.
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return ""
        return str(valor)
        
    def classify_cause(message: str, exception_type: str = "") -> str:
        # El tipo de excepción tiene prioridad: es más confiable que el
        # mensaje (p. ej. WebDriverTimeoutException es un timeout real,
        # mientras que un mensaje de Selenium puede contener "timeout" sin
        # que el fallo lo sea).
        exc = _texto(exception_type).lower()
        if "nosuchelement" in exc or "sessionnotcreated" in exc:
            return "🖥️ Infraestructura / Entorno de ejecución"
        if "timeoutexception" in exc or "webdrivertimeout" in exc:
            return "⏱️ Timeouts / Asincronía"
        text = _texto(message).lower()
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
                failed_tests["causa"] = failed_tests.apply(
                    lambda row: classify_cause(
                        row.get("exception_message"), row.get("exception_type")
                    ),
                    axis=1,
                )
                cause_matrix = (
                    failed_tests.groupby(["project", "causa"])
                    .size().reset_index(name="fallos")
                    .sort_values("fallos", ascending=False)
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

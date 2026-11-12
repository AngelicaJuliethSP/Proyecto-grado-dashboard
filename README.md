# Dashboard QA — Proyecto de Grado

Dashboard para la **visualización y análisis de reportes de ejecución de pruebas automatizadas**, integrado a un **pipeline de integración continua**, con el propósito de centralizar los resultados y facilitar el seguimiento de indicadores de calidad y estabilidad del proceso de automatización.

**🌐 Dashboard público: https://proyecto-grado-dashboard.streamlit.app**

## Arquitectura

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  SauceDemo (Web UI) │     │ WdioMobile (Mobile) │     │   PetStore (API)    │
│  Selenium + TestNG  │     │  Appium + TestNG    │     │ RestAssured + TestNG│
└──────────┬──────────┘     └──────────┬──────────┘     └──────────┬──────────┘
           │  GitHub Actions           │  GitHub Actions           │  GitHub Actions
           │  (push/PR/cron diario)    │  (push/PR/cron diario)    │  (push/PR/cron diario)
           ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              Cada pipeline parsea sus XML de Surefire y hace push            │
│              del consolidado a data/results.json de ESTE repositorio         │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Dashboard Streamlit (dashboard/app.py)                      │
│   KPIs · tendencia de éxito · pass/fail/skip · duración · top fallos        │
│   causa raíz · bottlenecks · flaky · detalle por test                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**El ciclo es 100% automático:** los 3 pipelines de CI (en sus repos
respectivos) ejecutan las suites a diario (cron 06:00 UTC =
01:00 Colombia), parsean sus reportes y publican los resultados en
`data/results.json` de este repositorio. Streamlit Community Cloud
redespliega automáticamente con cada push, por lo que el dashboard siempre
refleja el histórico actualizado — sin ningún paso manual.

> **Sobre el cron:** está programado a las **06:00 UTC** (01:00 Colombia),
> pero GitHub Actions puede iniciarlo **con horas de retraso** en momentos
> de alta carga (los eventos `schedule` no tienen garantía de puntualidad).
> El horario de cada registro del histórico es el de la ejecución real,
> no el del cron teórico.

## Estructura del repositorio

```
proyecto-grado-dashboard/
├── dashboard/
│   └── app.py                  # Dashboard Streamlit (11 vistas)
├── parser/
│   ├── results_parser.py       # Parser de testng-results.xml / TEST-*.xml
│   └── allure_ingest.py        # Ingesta de resultados Allure (JSON)
├── scripts/
│   └── run_baseline.py         # Ejecuta la línea base N veces e ingiere cada corrida
├── .streamlit/
│   └── config.toml             # Tema del dashboard (paleta azul)
├── data/
│   ├── results.json            # Histórico de ejecuciones (actualizado por CI)
│   └── results_backup.json     # Respaldo pre-línea-base (piloto, 4 ejecuciones)
├── tests/                      # Pruebas pytest del parser (14 casos)
├── docs/                       # Documentación técnica por fases
├── requirements.txt
└── README.md
```

> **Requisito:** Python 3.10 o superior (`allure_ingest.py` usa la sintaxis `int | None`, disponible desde 3.10). El despliegue en Streamlit Community Cloud usa Python 3.14.

## Proyectos de pruebas (repositorios independientes)

| Proyecto | Tipo | Stack |
|---|---|---|
| SauceDemoAutomation | Web UI | Java 17, Selenium 4.47, TestNG 7.10.2, POM |
| WdioMobileAutomation | Mobile | Java 17, Appium java-client 10.1.1, TestNG 7.10.2 |
| PetStoreRestAssured | API | Java 17, RestAssured 5.3.1, TestNG 7.10.2 |

> Los tres comparten Maven + TestNG. Web y API generan `testng-results.xml` y Wdio genera `TEST-*.xml` estilo JUnit (combinados por clase), y todos se procesan con un único parser.

> **Nota sobre la línea base:** las ejecuciones de la línea base (Fase 0) se ingirieron desde los JSON de **Allure** (`parser/allure_ingest.py`), no desde los XML de Surefire. El parser de Surefire se usa en el ciclo automático de CI; `allure_ingest.py` quedó como vía de ingesta para corridas locales con el adapter Allure activo.

## Configuración del flujo automático

Cada repo de pruebas necesita el secreto **`DASHBOARD_TOKEN`** (Settings →
Secrets and variables → Actions): un *fine-grained Personal Access Token*
con permiso **Contents: Read and write** sobre este repositorio. Sin el
secreto, el paso de publicación se omite gracefully y el pipeline no se ve
afectado.

## Uso local (opcional)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Generar resultados manualmente (opcional)

Tras ejecutar `mvn test` en cualquiera de los proyectos:

```bash
python parser/results_parser.py \
    --project SauceDemoAutomation \
    --reports-dir ../SauceDemoAutomation/target/surefire-reports \
    --output data/results.json
```

### 3. Levantar el dashboard

```bash
streamlit run dashboard/app.py
```

## Indicadores del dashboard

- **KPIs globales:** ejecuciones registradas, última tasa de éxito, tests, fallos y duración.
- **Tendencia histórica** de tasa de éxito por proyecto.
- **Comparativa entre suites** (éxito promedio, duración promedio).
- **Distribución pass/fail/skip** por ejecución.
- **Duración** de cada ejecución (detección de degradaciones).
- **Top 10 tests más fallidos** (candidatos a estabilización).
- **Matriz de causa raíz probable** (clasificación por patrones del mensaje de error).
- **Top bottlenecks** (tests más lentos, Pareto).
- **Pruebas inestables (flaky)** (tests que alternan entre éxito y fallo).
- **Detalle por test** con filtros y búsqueda.
- **Histórico completo** en tabla.

## Metas de calidad y semaforización

Las metas se definieron con el criterio: duraciones calibradas con los
tiempos habituales de cada suite en CI; web y API (entornos deterministas)
exigen 0 fallos y 100% de éxito; la móvil tolera 1 fallo (emulador de CI
intermitente) con éxito mínimo 75%, coherente con sus 4 pruebas. El máximo
de pruebas inestables (flaky) se evalúa sobre las **últimas 10 ejecuciones**
de cada suite, no sobre todo el histórico.

| Métrica | PetStore (API) | SauceDemo (Web) | WdioMobile (Mobile) |
|---|---|---|---|
| Fallos por ejecución | 0 | 0 | ≤ 1 |
| Tasa de éxito mínima | 100% | 100% | 75% |
| Duración máx. suite | 10 s | 30 s | 240 s |
| Duración máx. por test | 5 s | 10 s | 30 s |
| Flaky máx. (ventana 10) | 0 | 0 | 0 |

**Semáforo de la comparativa entre suites** (gráfica de éxito promedio):

| Color | Significado |
|---|---|
| 🟢 Verde | Cumple la meta de éxito |
| 🟠 Naranja | Cerca de la meta (dentro de 10 puntos porcentuales) |
| 🔴 Rojo | Lejos de la meta |

Adicionalmente: los fallidos que exceden la meta de la suite se pintan en
rojo en la tabla de resumen, y las duraciones que exceden su meta se marcan
con borde rojo conservando el color de la suite.

## Dependencias

Versiones fijadas en `requirements.txt`:

| Paquete | Versión | Uso |
|---|---|---|
| streamlit | 1.67.0 | Framework del dashboard |
| pandas | 3.1.1 | Manipulación del histórico |
| plotly | 7.1.0 | Gráficas interactivas |
| pytest | (sin fijar) | Pruebas del parser |

## Autor

Angélica Julieth Silva Pérez — College Trainee, Globant

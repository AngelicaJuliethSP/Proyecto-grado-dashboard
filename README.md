# Dashboard QA — Proyecto de Grado

Dashboard para la **visualización y análisis de reportes de ejecución de pruebas automatizadas**, integrado a un **pipeline de integración continua**, con el propósito de centralizar los resultados y facilitar el seguimiento de indicadores de calidad y estabilidad del proceso de automatización.

## Arquitectura

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  SauceDemo (Web UI) │     │ WdioMobile (Mobile) │     │   PetStore (API)    │
│  Selenium + TestNG  │     │  Appium + TestNG    │     │ RestAssured + TestNG│
└──────────┬──────────┘     └──────────┬──────────┘     └──────────┬──────────┘
           │  mvn test                 │  mvn test                 │  mvn test
           ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GitHub Actions — Pipeline de CI                          │
│  jobs paralelos → parser/results_parser.py → data/results.json (histórico)  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Dashboard Streamlit (dashboard/app.py)                      │
│   KPIs · tendencia de éxito · pass/fail/skip · duración · top fallos        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Estructura del repositorio

```
proyecto-grado-dashboard/
├── dashboard/
│   └── app.py                  # Dashboard Streamlit
├── parser/
│   └── results_parser.py       # Parser de testng-results.xml / TEST-*.xml
├── data/
│   └── results.json            # Histórico de ejecuciones (generado)
├── .github/workflows/
│   └── ci.yml                  # Pipeline de integración continua
├── requirements.txt
└── README.md
```

## Proyectos de pruebas (repositorios independientes)

| Proyecto | Tipo | Stack |
|---|---|---|
| SauceDemoAutomation | Web UI | Java 17, Selenium 4.47, TestNG 7.5, POM |
| WdioMobileAutomation | Mobile | Java 17, Appium java-client 10.1.1, TestNG 7.10.2 |
| PetStoreRestAssured | API | Java 11, RestAssured 5.3.1, TestNG 7.10.2 |

> Los tres comparten Maven + TestNG, por lo que sus reportes de Surefire (`testng-results.xml`) se procesan con un único parser.

## Uso local

### 1. Instalar dependencias del dashboard

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

## Pipeline de CI

El workflow `.github/workflows/ci.yml`:

1. Ejecuta los 3 proyectos en jobs paralelos (`mvn test`).
2. Parsea los reportes de Surefire con `parser/results_parser.py`.
3. Consolida todo en `data/results.json` y lo commitea al histórico.

**Configuración previa:** reemplaza `<TU_USUARIO>` en `ci.yml` por tu usuario de GitHub en los 3 `actions/checkout` de los proyectos de pruebas.

## Indicadores del dashboard

- **KPIs globales:** ejecuciones registradas, última tasa de éxito, tests, fallos y duración.
- **Tendencia histórica** de tasa de éxito por proyecto.
- **Distribución pass/fail/skip** por ejecución.
- **Duración** de cada ejecución (detección de degradaciones).
- **Top 10 tests más fallidos** (candidatos a estabilización).
- **Histórico completo** en tabla.

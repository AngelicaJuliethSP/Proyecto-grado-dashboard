# Fase 4: Diseño y construcción del dashboard

## 1. Objetivo de la fase

Desarrollar un dashboard que muestre resultados históricos de las tres suites
de pruebas mediante indicadores y tendencias, e identifique variaciones de
calidad y pruebas inestables, cumpliendo el cuarto objetivo específico del
proyecto.

## 2. Stack tecnológico

| Tecnología | Rol | Justificación |
|---|---|---|
| **Python** | Lenguaje principal | Ecosistema de análisis de datos (pandas) y despliegue sencillo |
| **pandas** | Transformación de datos | Lectura del almacén JSON, agregaciones, detección de patrones |
| **Streamlit** | Framework de visualización | Desarrollo rápido, sin frontend, despliegue gratuito en Streamlit Community Cloud |

## 3. Arquitectura

```
GitHub Actions (3 repos, cron diario 06:00 UTC)
        │  ejecuta suites (Maven + TestNG)
        ▼
Surefire XML / Allure JSON  ──►  parser/ (results_parser.py, allure_ingest.py)
        │  consolida
        ▼
data/results.json  (almacén único de ejecuciones)
        │  lee con pandas
        ▼
dashboard/app.py (Streamlit)  ──►  URL pública
```

- **Origen de datos**: `data/results.json`, alimentado por el parser a partir
  de los reportes de cada ejecución (local o CI).
- **Actualización**: los pipelines corren una vez al día (cron `0 6 * * *`,
  01:00 hora Colombia) además de los triggers por push/PR/manual; cada
  ejecución nueva se consolida al almacén y el dashboard refleja la evolución.
- **Despliegue**: Streamlit Community Cloud, conectado al repositorio de
  GitHub — cada push a `main` redespliega automáticamente.

## 4. Vistas del dashboard

| # | Vista | Descripción | Indicador que soporta |
|---|---|---|---|
| 1 | **KPIs globales** | Ejecuciones registradas, última tasa de éxito, tests, fallos y duración de la última ejecución | Estado actual del proceso |
| 2 | **Tendencia de tasa de éxito** | Línea por suite a lo largo de las ejecuciones | Variaciones de calidad en el tiempo |
| 3 | **Comparativa entre suites** | Barras de % de éxito promedio + tabla agregada (tests, pasados, fallidos, duración prom.) | Calidad relativa Web/API/Mobile |
| 4 | **Resultados por ejecución** | Barras apiladas pasados/fallidos/omitidos | Comportamiento por corrida |
| 5 | **Duración de ejecuciones** | Barras de duración por corrida (execution drift) | Degradación de tiempos |
| 6 | **Tests más fallidos** | Top 10 histórico por número de fallos | Puntos críticos de las suites |
| 7 | **Matriz de causa raíz probable** | Clasificación automática de fallos por patrones del mensaje de error (regex): timeouts/asincronía, concurrencia, red, datos de prueba, aserciones, infraestructura | Análisis de fallos recurrentes |
| 8 | **Top bottlenecks** | Ranking de tests más lentos con % del tiempo total (Pareto) | Optimización de tiempos de CI |
| 9 | **Pruebas inestables (flaky)** | Tests que alternaron entre éxito y fallo entre ejecuciones | Identificación de inestabilidad |
| 10 | **Detalle por test** | Tabla filtrable por estado, suite y búsqueda por nombre/clase | Trazabilidad completa |
| 11 | **Histórico de ejecuciones** | Tabla de todas las corridas registradas | Auditoría |

Adicionalmente: encabezado con los objetivos del proyecto (general y
específicos), filtros laterales por proyecto y pie de página informativo.

## 5. Implementación

### 5.1 Estructura del código

`dashboard/app.py` (~430 líneas) organizado en:

- **Estilos personalizados** (CSS): encabezado con degradado, tarjetas de
  objetivos, métricas con borde, pie de página.
- **Carga de datos** con caché (`@st.cache_data`, TTL 30 s).
- **Vistas** renderizadas en orden, con divisores y subtítulos.

### 5.2 Clasificación de causa raíz

La matriz de causa raíz usa análisis de texto simple (regex) sobre el campo
`exception_message` de cada test fallido. Categorías y patrones principales:

| Categoría | Patrones (ejemplos) |
|---|---|
| Timeouts / Asincronía | `timeout`, `expected condition failed`, `waiting for` |
| Concurrencia | `stale element`, `not interactable` |
| Red / Dependencias externas | `connection refused`, `502/503/504` |
| Datos de prueba / Aislamiento | `duplicate`, `already exists`, `409` |
| Aserción (comportamiento) | `expected [`, `but found` |
| Infraestructura / Entorno | `session not created`, `webview`, `emulator`, `no such element` |

Verificado con el histórico real: 13 fallos mobile clasificados (12
timeouts/asincronía, 1 aserción de contenido no visible).

### 5.3 Detección de pruebas inestables

Un test se marca como *flaky* si en el histórico aparece con estado `passed`
y `failed` en ejecuciones distintas (agrupación por suite, clase y nombre).
En los datos actuales no hay flaky: los fallos mobile fueron consistentes
(limitación del entorno), lo cual es coherente con el diagnóstico de la línea
base.

## 6. Despliegue

| Aspecto | Detalle |
|---|---|
| Plataforma | Streamlit Community Cloud (gratuita) |
| Repositorio | `AngelicaJuliethSP/Proyecto-grado-dashboard` |
| URL pública | **https://proyecto-grado-dashboard.streamlit.app** |
| Redespliegue | Automático por push a `main` |
| Dependencias | `requirements.txt` (streamlit, pandas) |
| Tema | `.streamlit/config.toml` (paleta azul corporativa) |

## 7. Verificación

- Compilación sin errores (`py_compile`).
- Lógica de datos validada con el almacén real (10 ejecuciones, 58 filas de
  tests, 13 fallos clasificados).
- Verificación visual local del servidor (las 11 vistas renderizan).
- Despliegue en la nube verificado en la URL pública.

## 8. Criterios de salida cumplidos

| Criterio | Estado |
|---|---|
| Dashboard construido con vistas de indicadores y tendencias | ✅ (11 vistas) |
| Identificación de variaciones de calidad | ✅ (tendencia + comparativa) |
| Identificación de pruebas inestables | ✅ (vista flaky) |
| Análisis de fallos recurrentes | ✅ (matriz de causa raíz) |
| Acceso público al dashboard | ✅ (Streamlit Community Cloud) |
| Cambios versionados y publicados | ✅ (GitHub + redespliegue automático) |

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
| Infraestructura / Entorno | `session not created`, `could not start a new session`, `adbexec`, `no such element`, `emulator`, `webview` |
| Timeouts / Asincronía | `timeout`, `expected condition failed`, `waiting for` |
| Concurrencia | `stale element`, `not interactable` |
| Red / Dependencias externas | `connection refused`, `502/503/504` |
| Datos de prueba / Aislamiento | `duplicate`, `already exists`, `409` |
| Aserción (comportamiento) | `expected [`, `but found` |

Dos refinamientos sobre la primera versión del clasificador:

1. **Orden de evaluación**: *Infraestructura* se evalúa antes que *Timeouts*.
   Varios fallos de infraestructura contienen la palabra "timeout" en el
   mensaje de Selenium (p. ej. `Could not start a new session... adbExec
   timeout`, o `NoSuchElement` con `Command duration or timeout`) sin ser
   timeouts reales; al evaluarse Timeouts primero, quedaban mal clasificados.
2. **Tipo de excepción**: además del mensaje, el clasificador usa
   `exception_type` con prioridad (`NoSuchElementException` /
   `SessionNotCreatedException` → infraestructura; `TimeoutException` →
   timeouts), ya que el tipo es más confiable que el texto del mensaje.

Verificado con el histórico real al 9-nov 18:00 (38 fallos en 54 registros):
16 mobile de aserción (`navigateThroughBottomMenu`, contenido no visible por
la limitación de renderizado del emulador), 13 mobile de aserción
(`swipeCardsAndFindHiddenText`, misma causa), 6 web de infraestructura
(`NoSuchElement` en checkout, resuelto con waits explícitos), 1 web de
aserción (`removeAllItemsFromCart`), 1 timeout móvil (`TimeoutException` en
la corrida de debugging del 7-nov) y 1 error de código
(`IllegalArgumentException: bound must be positive`). Los 12 fallos de
`setUp` de la línea base (sesión Appium no creada) ya no se cuentan como
tests: se filtraron como configuraciones en la ingesta de Allure
(`allure_ingest.py`). El histórico sigue creciendo con cada corrida del CI,
por lo que estos conteos corresponden a la fecha de corte indicada.

### 5.3 Detección de pruebas inestables

Un test se marca como *flaky* si en el histórico aparece con estado `passed`
y `failed` en ejecuciones distintas (agrupación por suite, clase y nombre).
Con el criterio del propio dashboard, el histórico al 9-nov 17:00 registra
5 pruebas inestables:

- `purchaseProductSuccessfully` (SauceDemo): pasó en la mayoría de corridas y
  falló en varias del 8-nov y 9-nov (`NoSuchElement` en checkout por clicks
  perdidos en React; corregido con waits explícitos).
- `removeAllItemsFromCart` (SauceDemo): falló una vez en el CI del 8-nov
  (`Expected 3 items in the cart before removal`); en el resto pasó.
- `successfulLogin` y `successfulSignUp` (Wdio): pasan en casi todas las
  corridas; fallaron solo en la corrida de debugging del 7-nov
  (`TimeoutException` esperando visibilidad de elementos).
- `swipeCardsAndFindHiddenText` (Wdio): falló en el piloto del 4-nov, pasó en
  la corrida del 7-nov (emulador en mejor estado) y vuelve a fallar en CI por
  la limitación de renderizado del emulador (SwiftShader).

`navigateThroughBottomMenu`, en cambio, no es flaky bajo este criterio: nunca
pasó en el histórico registrado (solo `failed` y `skipped`), por lo que es un
fallo consistente y no una alternancia éxito/fallo.

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

## 9. Limitaciones conocidas

- **Histórico corto**: el almacén acumula ~20 ejecuciones de 4 días (6 al 9 de
  noviembre de 2026). Es suficiente para validar el mecanismo, pero las
  "tendencias" que muestra el dashboard deben leerse como **tendencia inicial**
  y no como comportamiento estable: se requieren más corridas acumuladas antes
  de la sustentación para afirmaciones de tendencia robustas.
- **Fuentes de reportes mezcladas**: la línea base se registró parseando
  resultados de Allure y el CI parsea XML de Surefire; los campos disponibles
  difieren (p. ej. `started_at` solo existe en TestNG/Surefire). Los registros
  se normalizan al mismo esquema, pero conviene declarar la diferencia de
  origen al interpretar duraciones y timestamps.
- **Zonas horarias heterogéneas**: los timestamps combinan UTC (CI) y hora
  local Colombia (corridas locales, -05:00). El dashboard los normaliza a UTC
  con `pd.to_datetime(..., utc=True)`, pero la comparación horaria entre
  corridas locales y de CI tiene esa diferencia de origen.
- **Duplicados móviles corregidos**: hasta el 9-nov cada corrida móvil generó
  2 registros (uno por paso del pipeline); corregido para publicar un solo
  registro combinado por corrida. Los registros históricos anteriores se
  conservan tal cual (no se reescriben datos ya publicados).
- **Esquema del histórico móvil unificado (9-nov)**: las corridas del 8-nov ya
  tenían un solo registro de 4 tests, pero las del 9-nov (10:18, 10:47 y 12:30)
  seguían publicando 2 registros (uno de 2 tests al 100 % y otro de 2 tests al
  0 %), y la corrida de las 12:32 publicó solo 2 tests (1/1) perdiendo Login y
  Signup. Causa raíz: Surefire+TestNG nombra `TEST-TestSuite.xml` en ambos pasos
  del pipeline y el `cp` sin prefijo hacía que el segundo sobrescribiera al
  primero. Corregido en el workflow copiando con prefijo (`TEST-main-*`,
  `TEST-known-*`). Los 7 registros incompletos del 9-nov se eliminaron y las 5
  corridas se regeneraron con el parser a partir de los XML Surefire reales de
  los artefactos del CI. Resultados reales: 2/4 en las 3 primeras corridas
  (Login+Signup pasan, Swipe+Navigation fallan) y 3/4 en las 2 últimas
  (Login+Signup+Swipe pasan, Navigation falla).

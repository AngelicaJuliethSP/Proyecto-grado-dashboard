# Manual Técnico — Proyecto de Grado

**Integración de pruebas automatizadas (Web, API y Mobile) a un pipeline de integración continua con dashboard de indicadores**

Autora: Angélica Julieth Silva Pérez — College Trainee, Globant
Fecha: Noviembre de 2026

---

## 1. Introducción y alcance

Este manual documenta la solución técnica completa del proyecto de grado: tres
frameworks de automatización de pruebas (Web UI, API REST y Mobile Android),
el pipeline de integración continua que los ejecuta, el parser que consolida
los resultados y el dashboard web que los visualiza.

**Audiencia:** evaluadores, tutores y desarrolladores que necesiten entender,
mantener o extender la solución.

**Repositorios:**

| Repositorio | Contenido |
|---|---|
| `SauceDemoAutomation` | Framework de pruebas Web UI (Selenium) |
| `PetStoreRestAssured` | Framework de pruebas API REST (Rest Assured) |
| `WdioMobileAutomation` | Framework de pruebas Mobile (Appium) |
| `Proyecto-grado-dashboard` | Parser, almacén de resultados y dashboard |

**URL pública del dashboard:** https://proyecto-grado-dashboard.streamlit.app

### 1.1 Declaración sobre el uso de herramientas de IA

Durante el desarrollo de este proyecto se utilizó el asistente de código
**CODA** (Globant) como herramienta de apoyo en tareas de programación:
refactorización de los frameworks, configuración de los pipelines de CI,
construcción del parser, del dashboard y de este documento. Cada commit
asistido lleva la co-firma `Co-Authored-By: CODA <coda@globant.com>` en el
historial de Git, como declaración explícita de la herramienta empleada.
Al corte del 12-nov-2026, los commits co-firmados con CODA son:
`SauceDemoAutomation` 17 de 39, `PetStoreRestAssured` 14 de 30,
`WdioMobileAutomation` 24 de 47 y `Proyecto-grado-dashboard` 64 de 111
(122 de 227 en total).

Las decisiones de arquitectura, el alcance de cada fase, la interpretación de
resultados y la validación final son de la autora. La herramienta actuó como
asistente de implementación bajo dirección humana, de forma análoga a un
par de programación. Se declara este uso en cumplimiento de la transparencia
académica; la autora verificó la política de la institución (UCC) sobre uso
de IA en trabajos de grado antes de la entrega.

## 2. Arquitectura general

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
│              del consolidado a data/results.json del repositorio dashboard   │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  Dashboard Streamlit (dashboard/app.py)                      │
│   KPIs · tendencia de éxito · pass/fail/skip · duración · top fallos        │
│   causa raíz · bottlenecks · flaky · detalle por test                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Decisiones de arquitectura clave:**

1. **Repositorios independientes por suite** — cada framework evoluciona y se
   ejecuta por separado, reflejando un escenario real de automatización.
2. **Un único parser** — los tres frameworks comparten Maven + TestNG, por lo
   que sus reportes de Surefire (`testng-results.xml`) tienen el mismo
   formato y se procesan con un solo componente.
3. **Almacén único consolidado** — `data/results.json` en el repositorio del
   dashboard centraliza el histórico de todas las suites.
4. **Publicación desde el CI** — cada pipeline publica sus propios resultados
   al final de la corrida (con `if: always()`, incluso si la suite falla),
   eliminando pasos manuales.
5. **Redespliegue automático** — Streamlit Community Cloud redespliega el
   dashboard con cada push al repositorio.

## 3. Stack tecnológico común

| Tecnología | Versión | Rol |
|---|---|---|
| Java | 17 | Lenguaje de los tres frameworks |
| Maven | 3.9+ | Gestión de dependencias y ejecución |
| TestNG | 7.10.2 | Framework de pruebas y aserciones |
| Maven Surefire | 3.1.2 | Plugin de ejecución y generación de XML |
| Allure TestNG | 2.29.1 | Adaptador de resultados para reportes |
| GitHub Actions | — | Pipeline de integración continua |
| Python | 3.10+ | Parser y dashboard (`allure_ingest.py` usa `int | None`, disponible desde 3.10; el despliegue en Streamlit Cloud usa 3.14) |
| pandas | 3.1.1 | Transformación de datos |
| Streamlit | 1.67.0 | Dashboard web |
| plotly | 7.1.0 | Gráficas interactivas del dashboard |

## 4. Framework Web UI — SauceDemoAutomation

Automatización de la tienda virtual [saucedemo.com](https://www.saucedemo.com)
con Selenium WebDriver y patrón Page Object.

### 4.1 Stack específico

| Tecnología | Versión | Rol |
|---|---|---|
| Selenium Java | 4.47.0 | Automatización del navegador |
| WebDriverManager | 5.8.2 | Gestión del driver de Chrome |

### 4.2 Estructura

```
src/test/java/com/saucedemo/
├── base/
│   ├── BasePage.java       # WebDriverWait compartido, waitForVisible
│   └── BaseTest.java       # setUp/tearDown, headless y BASE_URL externalizados
├── listeners/
│   └── ScreenshotListener.java  # captura en fallo
├── pages/                  # Page Objects (Login, Inventory, Cart, Checkout x3)
└── tests/                  # Login, Purchase, RemoveCartItems, Logout
```

### 4.3 Decisiones de diseño

- **Page Object Model estricto**: cada página es una clase; los tests no
  conocen localizadores.
- **Waits explícitos compartidos** en `BasePage` (lección de la fase de
  reportes: sin waits, los clicks se pierden en React y fallan escenarios con
  usuarios de performance).
- **Configuración externalizada** con prioridad `-Dprop` > variable de
  entorno > default: `headless`, `base.url`.
- **Listener de capturas** en fallo para evidencia.

### 4.4 Ejecución

```bash
mvn clean test -Dheadless=true -Dbase.url=https://www.saucedemo.com/
```

## 5. Framework API — PetStoreRestAssured

Pruebas del API REST de [petstore.swagger.io](https://petstore.swagger.io/v2)
con Rest Assured y modelo de datos tipado.

### 5.1 Stack específico

| Tecnología | Versión | Rol |
|---|---|---|
| Rest Assured | 5.3.1 | Cliente HTTP y aserciones de respuesta |
| Jackson | 2.17.2 | Serialización POJO ↔ JSON |

### 5.2 Estructura

```
src/test/java/com/globant/automation/
├── config/TestRunner.java  # configuración base
├── model/                  # POJOs (Pet, Order, User, Category, Tag, ApiResponse)
├── request/RequestBuilder.java  # construcción de peticiones
└── test/                   # 6 suites: pets, orders, users, login/logout
```

### 5.3 Decisiones de diseño

- **Modelo tipado**: las respuestas se deserializan a POJOs, las aserciones
  son sobre objetos y no sobre JSON crudo.
- **RequestBuilder centralizado**: especificación de petición reutilizable
  (base URI, content type, logging).

### 5.4 Ejecución

```bash
mvn clean test
```

## 6. Framework Mobile — WdioMobileAutomation

Pruebas de la app nativa Android
[webdriverio/native-demo-app](https://github.com/webdriverio/native-demo-app)
con Appium.

### 6.1 Stack específico

| Tecnología | Versión | Rol |
|---|---|---|
| Appium java-client | 10.1.1 | Cliente Appium |
| Appium server | 3.9.0 | Servidor de automatización |
| uiautomator2 | 8.7.3 | Driver Android |

### 6.2 Estructura

```
src/test/java/
├── base/BaseTest.java      # sesión Appium, capabilities
├── drivers/DriverManager.java   # externalización de config, resolución de APK
├── screens/                # Screen Objects (Home, Login, Forms, Swipe, Drag, Web, Menu)
├── tests/                  # Login, Signup, Navigation, Swipe
└── utils/DataGenerator.java     # datos de prueba dinámicos
```

### 6.3 Decisiones de diseño

- **Screen Object Model** (equivalente mobile del POM).
- **DriverManager externalizado**: plataforma, device name, versión de Android
  y ruta del APK con prioridad `-Dprop` > env var > default; el APK se
  resuelve a ruta absoluta y se valida su existencia (las rutas relativas se
  resuelven contra el CWD del servidor Appium, no del proyecto).
- **Escenarios de renderizado excluidos del CI**: `NavigationTest` y
  `SwipeTest` son intermitentes en emuladores con renderizado por software
  (SwiftShader); se ejecutan en paso separado con
  `maven.test.failure.ignore=true` para registrarlos como fallos conocidos sin
  romper el pipeline.

### 6.4 Ejecución

```bash
# con emulador Android corriendo y Appium activo:
mvn clean test -Dplatform.name=Android -Ddevice.name=Pixel_6 -Dapk.path=/ruta/app.apk
```

## 7. Pipeline de integración continua

Cada repositorio de pruebas tiene su workflow
`.github/workflows/ci.yml` con los triggers: push a `main`, pull request a
`main`, ejecución manual (`workflow_dispatch`) y **cron diario**
(`0 6 * * *` = 01:00 hora Colombia).

### 7.1 Resumen de pipelines

| Pipeline | Runner | Particularidades |
|---|---|---|
| Web (SauceDemo) | `ubuntu-latest` | Chrome headless incluido en el runner |
| API (PetStore) | `ubuntu-latest` | Solo requiere acceso a internet |
| Mobile (WdioMobile) | `ubuntu-latest` | Emulador Android API 30 (Pixel 6) vía `reactivecircus/android-emulator-runner`, Appium 3.9.0 + uiautomator2 8.7.3, APK de los releases de la app demo |

### 7.2 Artefactos por corrida

| Artefacto | Descripción | Retención |
|---|---|---|
| `surefire-reports-{web,api,mobile}` | XML de Surefire | 7 días |
| `allure-results-{web,api,mobile}` | Resultados Allure crudos | 7 días |
| `allure-report-{web,api,mobile}` | Reporte Allure HTML navegable | 7 días |
| `appium-log` (solo mobile) | Log del servidor Appium | 7 días |

### 7.3 Publicación automática al dashboard

Paso final de cada pipeline (`if: always()`, corre incluso si la suite falla):

1. Verifica el secreto `DASHBOARD_TOKEN` (fine-grained PAT, permiso
   *Contents: Read and write* sobre el repo del dashboard). Si falta, se
   omite gracefully.
2. Clona el repositorio del dashboard.
3. Ejecuta `parser/results_parser.py` sobre los XML de Surefire con
   `--executed-at` (timestamp real de la corrida).
4. Hace commit y push de `data/results.json` si hubo cambios.
5. Streamlit Cloud redespliega el dashboard automáticamente.

**Configuración del secreto** (por cada repo de pruebas): Settings →
Secrets and variables → Actions → New repository secret → nombre
`DASHBOARD_TOKEN`, valor = PAT.

## 8. Parser de resultados

`parser/results_parser.py` convierte los reportes de Maven Surefire
(`testng-results.xml` y/o `TEST-*.xml` estilo JUnit) en un JSON normalizado.

**Registro por ejecución:**

```json
{
  "project": "SauceDemoAutomation",
  "executed_at": "2026-11-08T13:58:20-05:00",
  "total": 12, "passed": 11, "failed": 1, "skipped": 0,
  "duration_ms": 45230,
  "tests": [
    {"name": "...", "class": "...", "status": "passed",
     "duration_ms": 1234, "exception_message": null}
  ]
}
```

**Funciones clave:**

- `parse_reports_dir()` — lee todos los XML del directorio de reportes.
- `append_to_store()` — agrega la ejecución al histórico con **deduplicación
  por `(project, executed_at)`** (re-ejecuciones no duplican registros).
- `main()` — CLI con `--project`, `--reports-dir`, `--output`,
  `--executed-at`.

## 9. Dashboard de indicadores

`dashboard/app.py` (Streamlit) lee `data/results.json` con pandas y expone
11 vistas:

| # | Vista | Indicador que soporta |
|---|---|---|
| 1 | KPIs globales | Estado actual del proceso |
| 2 | Tendencia de tasa de éxito | Variaciones de calidad en el tiempo |
| 3 | Comparativa entre suites | Calidad relativa Web/API/Mobile |
| 4 | Resultados por ejecución | Comportamiento por corrida |
| 5 | Duración de ejecuciones | Degradación de tiempos |
| 6 | Tests más fallidos | Puntos críticos de las suites |
| 7 | Matriz de causa raíz probable | Análisis de fallos recurrentes (regex sobre `exception_message`) |
| 8 | Top bottlenecks | Optimización de tiempos de CI (Pareto) |
| 9 | Pruebas inestables (flaky) | Identificación de inestabilidad |
| 10 | Detalle por test | Trazabilidad completa |
| 11 | Histórico de ejecuciones | Auditoría |

**Despliegue:** Streamlit Community Cloud, conectado al repositorio de
GitHub — cada push a `main` redespliega automáticamente. Configuración de
tema en `.streamlit/config.toml`.

### 9.1 Metas de calidad y semaforización

Las metas se definieron con el criterio: duraciones calibradas con los
tiempos habituales de cada suite en CI; web y API (entornos deterministas)
exigen 0 fallos y 100% de éxito; la móvil tolera 1 fallo (emulador de CI
intermitente) con éxito mínimo 75%, coherente con sus 4 pruebas. El máximo
de pruebas inestables (flaky_max = 0) se evalúa sobre las últimas 10
ejecuciones de cada suite.

| Métrica | PetStore (API) | SauceDemo (Web) | WdioMobile (Mobile) |
|---|---|---|---|
| Fallos por ejecución | 0 | 0 | ≤ 1 |
| Tasa de éxito mínima | 100% | 100% | 75% |
| Duración máx. suite | 10 s | 30 s | 240 s |
| Duración máx. por test | 5 s | 10 s | 30 s |
| Flaky máx. (ventana 10) | 0 | 0 | 0 |

**Semáforo de la comparativa entre suites:** 🟢 verde = cumple la meta de
éxito; 🟠 naranja = cerca de la meta (dentro de 10 puntos porcentuales);
🔴 rojo = lejos de la meta. Los fallidos que exceden la meta se pintan en
rojo en la tabla de resumen.

## 10. Mantenimiento y extensión

### 10.1 Agregar un test nuevo

1. Crear la clase en `tests/` del framework correspondiente (respetando el
   patrón Page/Screen Object).
2. Verificar localmente: `mvn clean test -Dtest=MiTest`.
3. El CI lo ejecutará automáticamente en la siguiente corrida y publicará sus
   resultados al dashboard.

### 10.2 Agregar una vista al dashboard

1. Agregar la función de render en `dashboard/app.py` (patrón: función
   `render_xxx(df)` con `st.subheader` + gráfico Streamlit/Altair).
2. Registrarla en el selector de vistas.
3. El push redespliega el dashboard automáticamente.

### 10.3 Rotación del DASHBOARD_TOKEN

El PAT tiene expiración (90 días por defecto). Para rotarlo:

1. Generar un nuevo PAT con los mismos permisos.
2. Actualizar el secreto `DASHBOARD_TOKEN` en los 3 repos de pruebas.
3. Eliminar el PAT anterior.

### 10.4 Solución de problemas comunes

| Síntoma | Causa probable | Acción |
|---|---|---|
| El paso de publicación se omite | Falta el secreto `DASHBOARD_TOKEN` | Configurarlo en el repo |
| `unrecognized arguments: --executed-at` | El repo del dashboard tiene el parser viejo | Commitear y pushear el parser antes que los workflows |
| Tests web fallan en CI pero pasan local | Diferencias de entorno (resolución, timing) | Revisar waits explícitos; correr headless local |
| Mobile: sesión Appium 500 | Driver uiautomator2 viejo vs API de Android | Appium 3.9.0 + uiautomator2 8.7.3 |
| Dashboard no se actualiza | Sin push a `main` del repo dashboard | Verificar commits del bot en el histórico |

## 11. Referencias

- Documentación por fases: `docs/fase1..fase4` y `docs/linea_base.md` en este repositorio.
- Allure TestNG: https://allurereport.org/docs/testng/
- Streamlit: https://docs.streamlit.io
- Appium java-client: https://appium.github.io/java-client/
- Rest Assured: https://rest-assured.io
- Selenium: https://www.selenium.dev/documentation/

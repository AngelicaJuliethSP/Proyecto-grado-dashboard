# Fase 2: Pipeline de integración continua con GitHub Actions

## 1. Objetivo de la fase

Automatizar la ejecución de las tres suites de pruebas (Web, API y Mobile) en un
pipeline de integración continua, de modo que cada cambio en los repositorios se
compile y se valide automáticamente, generando evidencia de ejecución (reportes
y resultados) consumible por las fases siguientes.

## 2. Alcance

| Proyecto | Tipo | Pipeline | Trigger |
|---|---|---|---|
| `SauceDemoAutomation` | Web (Selenium) | CI - SauceDemo Web Tests | push/PR a `main` + manual + cron diario |
| `PetStoreRestAssured` | API (Rest Assured) | CI - PetStore API Tests | push/PR a `main` + manual + cron diario |
| `WdioMobileAutomation` | Mobile (Appium) | CI - WdioMobile Android Tests | push/PR a `main` + manual + cron diario |

Cada repositorio cuenta con su propio workflow (`.github/workflows/ci.yml`),
responsable de su suite. La consolidación de resultados entre suites se realiza
en fases posteriores (herramienta de reportes y dashboard).

## 3. Estructura común de los pipelines

Los tres workflows comparten una estructura base:

1. **Checkout** del repositorio (`actions/checkout@v4`).
2. **JDK 17 (Temurin)** con caché de Maven (`actions/setup-java@v4`), lo que
   acelera las ejecuciones al reutilizar el repositorio local de dependencias.
3. **Ejecución de la suite** con `mvn clean test -B` (modo batch, sin output
   interactivo).
4. **Publicación de artefactos** con `if: always()` (se publican aunque la suite
   falle, para poder depurar):
   - Reportes Surefire (`target/surefire-reports/`).
   - Resultados Allure (`target/allure-results/`).
   - Retención: 7 días.

Los triggers configurados en los tres casos son: push a `main`, pull request a
`main`, ejecución manual (`workflow_dispatch`) y **programación diaria**
(`schedule` con cron `0 6 * * *`, equivalente a las 01:00 hora Colombia), que
alimenta el histórico del dashboard con ejecuciones periódicas.

## 4. Pipeline Web (SauceDemoAutomation)

El pipeline web es el más simple: el runner de GitHub (`ubuntu-latest`) incluye
Google Chrome, y Selenium Manager resuelve el ChromeDriver automáticamente, por
lo que no se requiere instalación adicional.

```yaml
- name: Run tests (Chrome headless)
  run: mvn clean test -B -Dheadless=true
```

La configuración externalizada en la fase anterior (`-Dheadless=true`) es la que
permite ejecutar el navegador sin interfaz gráfica en el runner.

## 5. Pipeline API (PetStoreRestAssured)

El pipeline API tampoco requiere servicios externos: la suite apunta a la API
pública de Petstore (`https://petstore.swagger.io/v2`, configurada en
`config.properties`), accesible desde el runner.

```yaml
- name: Run API tests
  run: mvn clean test -B
```

## 6. Pipeline Mobile (WdioMobileAutomation)

El pipeline mobile es el más complejo, por la naturaleza del entorno: requiere
un emulador Android, un servidor Appium y el APK de la aplicación bajo prueba.

### 6.1 Componentes

| Componente | Versión | Instalación |
|---|---|---|
| Emulador Android | API 30, Pixel 6, x86_64 | `reactivecircus/android-emulator-runner@v2` |
| Appium Server | 3.9.0 | `npm install -g appium@3.9.0` |
| Driver UiAutomator2 | 8.7.3 | `appium driver install uiautomator2` |
| APK de la app | v2.2.0 | Descarga desde releases de `webdriverio/native-demo-app` |

### 6.2 Pasos del pipeline

1. **Descarga del APK** desde los releases públicos de la app de demo
   (el APK no está versionado en el repositorio por su tamaño, ~60 MB).
2. **Habilitación de KVM** (reglas udev) para acelerar la virtualización x86_64
   en el runner.
3. **Arranque de Appium** en segundo plano con verificación de disponibilidad
   (`/status` → `"ready":true`); el paso falla explícitamente si el servidor
   nunca queda listo.
4. **Ejecución de la suite** dentro del `android-emulator-runner`, que crea el
   emulador, espera el boot y ejecuta el script de Maven contra él.

### 6.3 Evolución de los escenarios mobile (antecedente y estado final)

Durante la puesta a punto inicial, dos escenarios mobile (`NavigationTest`,
`SwipeTest`) fallaban de forma intermitente en el emulador de CI. En su
momento se implementó una estrategia de dos pasos: un paso principal
(`LoginTest`, `SignupTest`, CI estricto) y un paso de "fallas conocidas" con
`-Dmaven.test.failure.ignore=true` que registraba la falla en los reportes
sin romper el pipeline. Esa etapa se conservó como antecedente; la hipótesis
de entonces (limitación del renderizado por software del emulador) quedó
**refutada** en el diagnóstico posterior.

**Causa real** (diagnosticada el 11-nov con logs de Appium y dumps de
uiautomator): no era el entorno de CI, sino dos defectos del propio framework
de pruebas — aserciones ejecutadas antes de que la pantalla terminara de
cargar (fix: esperas explícitas tras cada tap, commit `6b17dae`) y un gesto
de swipe que no alcanzaba a mover el carrusel o caía en la zona del gesto
"atrás" de Android (fix: gesto nativo `mobile: swipeGesture` de uiautomator2
y margen del 10%, commit `b6383ef`).

**Estado final (desde el 11-nov-2026):** las 4 pruebas mobile pasan de forma
estable y el workflow quedó **unificado en un solo paso** (`mvn clean test -B`
sin exclusiones ni tolerancia de fallas), con un único directorio de reportes
Surefire y publicación simplificada al dashboard. El emulador lento de CI solo
actuó como amplificador de un problema que existía en el código de pruebas.

## 7. Incidencias y depuración

La puesta a punto del pipeline mobile requirió cuatro iteraciones, documentadas
por su valor de aprendizaje:

1. **Instalación del driver de Appium**: la instalación vía
   `npm install -g appium-uiautomator2-driver` no registra el driver ante el
   servidor; debe usarse el comando propio `appium driver install uiautomator2`.
   Se agregó además una verificación explícita de disponibilidad del servidor
   (`/status`) que falla el paso si Appium nunca queda listo.
2. **Versión del emulador (API 34)**: la aplicación de demo no renderiza sus
   pantallas sobre API 34 en el runner (ni siquiera la pantalla Home). Se
   revirtió a API 30, donde la app funciona correctamente.
3. **Tiempos de espera**: el wait de 10 segundos de `BaseScreen` resultó
   insuficiente bajo el renderizado por software del runner (más lento que un
   emulador local con GPU). Se aumentó a 25 segundos.
4. **Intermitencia de Swipe**: los gestos de swipe no se procesan de forma
   confiable bajo SwiftShader. Como decisión **temporal** (hasta el
   11-nov-2026), Navigation y Swipe se ejecutaron en un paso separado con
   `maven.test.failure.ignore=true`, dejando la falla registrada en los
   reportes como **falla conocida documentada** (sección 6.3) en lugar de
   excluirlos del CI. El diagnóstico posterior (11-nov) determinó que la
   causa real no era el renderizado por software sino dos defectos del código
   de pruebas — aserciones ejecutadas antes de que la pantalla terminara de
   cargar y un gesto de swipe insuficiente —, corregidos con esperas
   explícitas (commit `6b17dae`) y el gesto nativo `mobile: swipeGesture`
   (commit `b6383ef`); desde entonces el workflow está **unificado en un solo
   paso** con CI estricto para las 4 pruebas.

Los pipelines web y API quedaron en verde en su primera ejecución.

## 8. Resultados de la fase

Estado final de los tres pipelines (verificado tras la última ejecución):

| Repositorio | Pipeline | Resultado |
|---|---|---|
| `SauceDemoAutomation` | CI - SauceDemo Web Tests | ✅ success |
| `PetStoreRestAssured` | CI - PetStore API Tests | ✅ success |
| `WdioMobileAutomation` | CI - WdioMobile Android Tests | ✅ success (las 4 pruebas en un solo paso, desde el 11-nov) |

Cada ejecución genera como artefactos los reportes Surefire y los resultados
Allure de la suite, con 7 días de retención.

## 9. Entregables de la fase

| Entregable | Descripción |
|---|---|
| `SauceDemoAutomation/.github/workflows/ci.yml` | Pipeline web (Chrome headless) |
| `PetStoreRestAssured/.github/workflows/ci.yml` | Pipeline API (Rest Assured) |
| `WdioMobileAutomation/.github/workflows/ci.yml` | Pipeline mobile (emulador Android + Appium) |
| `WdioMobileAutomation/src/test/java/screens/BaseScreen.java` | Wait aumentado a 25s para entornos de renderizado lento |
| Artefactos de CI | Reportes Surefire + resultados Allure por ejecución (7 días) |

## 10. Conclusiones

- El pipeline de integración continua quedó **operativo de extremo a extremo**:
  cada push a `main` dispara la compilación y ejecución automática de las tres
  suites, con publicación de evidencia.
- La externalización de configuración de la Fase 1 fue el habilitador directo
  de esta fase: los mismos comandos funcionan en local y en CI sin cambios de
  código.
- La depuración del pipeline mobile dejó documentadas tres lecciones
  reutilizables: registro de drivers de Appium, sensibilidad de la app a la
  versión de API, y ajuste de waits para renderizado por software.
- La intermitencia mobile (Navigation, Swipe) quedó **resuelta y documentada**:
  la causa real eran defectos del código de pruebas (aserciones prematuras y
  gesto de swipe insuficiente), corregidos con esperas explícitas y el gesto
  nativo `mobile: swipeGesture`; el workflow se unificó en un solo paso con
  CI estricto para las 4 pruebas.

## 11. Criterios de salida cumplidos

| Criterio | Estado |
|---|---|
| Pipeline automático por push/PR en los 3 repositorios | ✅ |
| Ejecución en verde de los pipelines | ✅ (Web, API y Mobile) |
| Evidencia de ejecución publicada como artefactos | ✅ (Surefire + Allure) |
| Intermitencia mobile diagnosticada, resuelta y documentada | ✅ (Navigation, Swipe — workflow unificado + README) |
| Cambios versionados y publicados en los repositorios | ✅ |

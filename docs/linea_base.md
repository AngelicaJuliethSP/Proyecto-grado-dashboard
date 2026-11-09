# Línea Base — Proyecto de Grado

**Fase 0: Diagnóstico y línea base**
Fecha de ejecución: 2026-11-06
Metodología: cada suite se ejecutó localmente 3 veces consecutivas, sin modificar el código de pruebas, con limpieza de `allure-results/` entre corridas para garantizar independencia de cada ejecución.

## 1. Entorno de ejecución

| Componente | Versión / Detalle |
|---|---|
| SO | Windows 11 (máquina local Angelica) |
| JDK | Temurin 17.0.20.1 |
| Maven | 3.10.0-rc-1 |
| Allure TestNG adapter | 2.29.1 |
| Emulador Android | Pixel_6, API 37.1 (google_apis_ps16k), headless SwiftShader |
| Appium | 3.7.0 (driver uiautomator2 8.6.1) |
| APK mobile | android.wdio.native.app.v2.2.0 (WebDriverIO native demo) |

## 2. Resultados por suite

### 2.1 SauceDemoAutomation (Web UI — Selenium)

| Corrida | Tests | Pasados | Fallados | % Éxito | Duración (pared Maven)* |
|---|---|---|---|---|---|
| 1 | 4 | 4 | 0 | 100% | ~44 s |
| 2 | 4 | 4 | 0 | 100% | ~46 s |
| 3 | 4 | 4 | 0 | 100% | ~52 s |

\* Las duraciones de esta sección son **tiempo de pared de Maven** (desde la invocación de `mvn` hasta su salida, incluye compilación y arranque de JVM/driver). No confundir con `duration_ms` del almacén `data/results.json`, que es el tiempo de ejecución de los tests según TestNG (12–14 s en SauceDemo, 7–8 s en PetStore): la diferencia es el overhead de Maven (compilación, inicialización del driver, teardown).

### 2.2 PetStoreRestAssured (API)

| Corrida | Tests | Pasados | Fallados | % Éxito | Duración (pared Maven)* |
|---|---|---|---|---|---|
| 1 | 6 | 6 | 0 | 100% | ~25 s |
| 2 | 6 | 6 | 0 | 100% | ~25 s |
| 3 | 6 | 6 | 0 | 100% | ~25 s |

\* Mismo criterio que la sección anterior: tiempo de pared de Maven. El tiempo de tests según TestNG (`duration_ms` en `data/results.json`) es de 7–8 s por corrida.

### 2.3 WdioMobileAutomation (Mobile — Appium)

| Corrida | Tests | Pasados | Fallados | Skipped | % Éxito | Observación |
|---|---|---|---|---|---|---|
| previa (piloto 4-nov) | 4 | 2 | 2 | 0 | 50% | Login/Signup OK; Navigation/Swipe fallan por renderizado |
| 1 | 8* | 0 | 4 | 4 | 0% | Fallo de sesión Appium (adbExec 500) |
| 2 | 8* | 0 | 4 | 4 | 0% | Fallo de sesión Appium |
| 3 | 8* | 0 | 4 | 4 | 0% | Fallo de sesión Appium |

\* El conteo de 8 incluye resultados residuales del directorio Allure (4 tests + 4 configuraciones setUp/tearDown contadas como tests). En cada corrida, los 4 tests reales quedaron: 4 fallidos por el fallo de sesión (los 4 omitidos del conteo son los `tearDown` que no llegaron a ejecutarse).

**Diagnóstico:** en la suite móvil, en cambio, ninguna de las tres ejecuciones pudo completarse: la sesión de Appium falló debido a una incompatibilidad entre el controlador (driver uiautomator2) y la imagen del emulador. En las ejecuciones previas a estas corridas, con el emulador en buen estado, la suite móvil había superado únicamente 2 de las 4 pruebas, ya que las dos restantes dependen del renderizado gráfico del emulador (véase el Anexo G). Se trata, por tanto, de fallos de infraestructura y no de fallos del framework de pruebas.

**Hallazgo clave para la tesis:** los tests mobile son sensibles a la estabilidad del entorno de ejecución (emulador). Esto motiva la ejecución mobile en el pipeline de CI con un emulador gestionado (`reactivecircus/android-emulator-runner`), donde el entorno se aprovisiona limpio en cada corrida.

## 3. Línea base consolidada

| Suite | Ejecuciones válidas | Tasa de éxito | Estabilidad |
|---|---|---|---|
| SauceDemoAutomation | 3 (+1 piloto) | 100% | Estable |
| PetStoreRestAssured | 3 (+1 piloto) | 100% | Estable |
| WdioMobileAutomation | 1 válida | 50% (2/4) | Inestable por entorno |

Nota: tras la línea base, una corrida posterior del piloto (7-nov, con el
emulador en mejor estado) registró 3/4 (75 %) — Swipe pasó; Navigation siguió
fallando por renderizado. Ambos registros (50 % y 75 %) son reales y
corresponden a corridas distintas; el 3/4 no invalida la línea base, confirma
la variabilidad del entorno móvil.

## 4. Punto de partida documentado

- **Web y API**: frameworks funcionan de punta a punta con reportes Allure; línea base 100%.
- **Mobile**: framework funcional (flujos nativos pasan); los tests que dependen de WebView/animaciones requieren entorno gráfico completo — se validará en CI.
- **Infraestructura de reportes**: Allure genera JSON nativo por test; la ingesta (`parser/allure_ingest.py`) consolida al almacén del dashboard.
- **Riesgo identificado**: dependencia del emulador local para mobile → mitigado en la fase de pipeline CI.

## 5. Evidencia

- Almacén de datos: `data/results.json` (20 ejecuciones registradas)
- Respaldo pre-línea-base: `data/results_backup.json`
- Script reproducible: `scripts/run_baseline.py --runs 3`

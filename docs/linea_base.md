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

| Corrida | Tests | Pasados | Fallados | % Éxito | Duración |
|---|---|---|---|---|---|
| 1 | 4 | 4 | 0 | 100% | ~44 s |
| 2 | 4 | 4 | 0 | 100% | ~46 s |
| 3 | 4 | 4 | 0 | 100% | ~52 s |

**Lectura:** suite estable — 12/12 tests pasados en 3 corridas consecutivas.

### 2.2 PetStoreRestAssured (API)

| Corrida | Tests | Pasados | Fallados | % Éxito |
|---|---|---|---|---|
| 1 | 6 | 6 | 0 | 100% |
| 2 | 6 | 6 | 0 | 100% |
| 3 | 6 | 6 | 0 | 100% |

**Lectura:** suite estable — 18/18 tests pasados. Tiempo promedio por corrida: ~25 s.

### 2.3 WdioMobileAutomation (Mobile — Appium)

| Corrida | Tests | Pasados | Fallados/Skipped | % Éxito | Observación |
|---|---|---|---|---|---|
| previa (piloto) | 4 | 2 | 2 | 50% | Login/Signup OK; Navigation/Swipe fallan por renderizado |
| 1 | 8* | 0 | 8 | 0% | Fallo de sesión Appium (adbExec 500) |
| 2 | 8* | 0 | 0 | 0% | Fallo de sesión Appium |
| 3 | 8* | 0 | 0 | 0% | Fallo de sesión Appium |

\* El conteo de 8 incluye resultados residuales del directorio Allure.

**Diagnóstico:** en la suite móvil, en cambio, ninguna de las tres ejecuciones pudo completarse: la sesión de Appium falló debido a una incompatibilidad entre el controlador (driver uiautomator2) y la imagen del emulador. En las ejecuciones previas a estas corridas, con el emulador en buen estado, la suite móvil había superado únicamente 2 de las 4 pruebas, ya que las dos restantes dependen del renderizado gráfico del emulador (véase el Anexo G). Se trata, por tanto, de fallos de infraestructura y no de fallos del framework de pruebas.

**Hallazgo clave para la tesis:** los tests mobile son sensibles a la estabilidad del entorno de ejecución (emulador). Esto motiva la ejecución mobile en el pipeline de CI con un emulador gestionado (`reactivecircus/android-emulator-runner`), donde el entorno se aprovisiona limpio en cada corrida.

## 3. Línea base consolidada

| Suite | Ejecuciones válidas | Tasa de éxito | Estabilidad |
|---|---|---|---|
| SauceDemoAutomation | 3 (+1 piloto) | 100% | Estable |
| PetStoreRestAssured | 3 (+1 piloto) | 100% | Estable |
| WdioMobileAutomation | 1 válida | 50% (2/4) | Inestable por entorno |

## 4. Punto de partida documentado

- **Web y API**: frameworks funcionan de punta a punta con reportes Allure; línea base 100%.
- **Mobile**: framework funcional (flujos nativos pasan); los tests que dependen de WebView/animaciones requieren entorno gráfico completo — se validará en CI.
- **Infraestructura de reportes**: Allure genera JSON nativo por test; la ingesta (`parser/allure_ingest.py`) consolida al almacén del dashboard.
- **Riesgo identificado**: dependencia del emulador local para mobile → mitigado en la fase de pipeline CI.

## 5. Evidencia

- Almacén de datos: `data/results.json` (9 ejecuciones registradas)
- Respaldo pre-línea-base: `data/results_backup.json`
- Script reproducible: `scripts/run_baseline.py --runs 3`

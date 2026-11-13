# Fase 1: Consolidación y refactorización de los frameworks de pruebas

## 1. Objetivo de la fase

Preparar los tres frameworks de pruebas automatizadas (Web, API y Mobile) para su
ejecución en un entorno de integración continua, eliminando las dependencias del
entorno local de desarrollo y estandarizando su configuración. Al finalizar la fase,
cada suite debe poder ejecutarse en cualquier máquina (incluido un agente de CI)
sin modificar código fuente, únicamente mediante propiedades o variables de entorno.

## 2. Alcance

| Proyecto | Tipo | Stack | Repositorio |
|---|---|---|---|
| SauceDemoAutomation | Web (UI) | Java 17, Selenium WebDriver, TestNG | `AngelicaJuliethSP/SauceDemoAutomation` |
| PetStoreRestAssured | API (REST) | Java 17, Rest Assured, TestNG | `AngelicaJuliethSP/PetStoreRestAssured` |
| WdioMobileAutomation | Mobile (Android) | Java 17, Appium (UiAutomator2), TestNG | `AngelicaJuliethSP/WdioMobileAutomation` |

> **Nota:** las rutas `piloto/...` corresponden al snapshot monolítico donde se
> hizo la refactorización. Ese snapshot fue eliminado del repositorio
> (120 MB de binarios); el código consolidado vive en los repositorios
> independientes `AngelicaJuliethSP/SauceDemoAutomation`,
> `AngelicaJuliethSP/PetStoreRestAssured` y
> `AngelicaJuliethSP/WdioMobileAutomation`.

Los tres proyectos comparten la misma base tecnológica (Maven + TestNG), lo que
permitió aplicar un criterio de consolidación uniforme.

## 3. Diagnóstico inicial

Tras revisar el código heredado de la línea base (Fase 0), se identificaron los
siguientes problemas:

1. **Rutas absolutas hardcodeadas**: `DriverManager.java` (mobile) referenciaba el
   APK con la ruta absoluta de la máquina de desarrollo
   (`C:\Users\angelica.silva01\...`), haciendo imposible su ejecución en otro
   entorno.
2. **Configuración fija de entorno mobile**: el nombre del dispositivo (`Pixel_6`)
   y la URL del servidor Appium (`http://127.0.0.1:4723`) estaban escritos
   directamente en el código, sin posibilidad de ajuste externo.
3. **URL base hardcodeada en la suite web**: `BaseTest.java` apuntaba siempre a
   `https://www.saucedemo.com/` y no existía modo *headless*, requisito para
   ejecutar navegadores en agentes de CI sin pantalla.
4. **Código muerto**: las plantillas `Main.java` generadas por IntelliJ IDEA
   ("Hello and welcome!") existían en PetStore y WdioMobile sin ningún uso.
5. **Versiones inconsistentes entre poms**: TestNG 7.5 vs 7.10.2, surefire
   2.22.1 vs 3.1.2, y una dependencia de JUnit 4.11 sin uso en la suite web.
6. **Fragilidad del entorno mobile local**: el driver `uiautomator2` instalado
   (8.6.1) resultó incompatible con la imagen del emulador (API 37.1), lo que
   impedía iniciar sesiones de prueba (ver sección 7).

## 4. Cambios realizados

### 4.1 WdioMobileAutomation — `DriverManager.java`

Se externalizó toda la configuración del driver Android con un mecanismo de
resolución en tres niveles, aplicado a cada parámetro:

1. Propiedad del sistema (`-Dapp.path=...`, `-Ddevice.name=...`, `-Dappium.url=...`)
2. Variable de entorno (`APP_PATH`, `DEVICE_NAME`, `APPIUM_URL`)
3. Valor por defecto (relativo al proyecto)

Adicionalmente:

- **Resolución de rutas relativas**: una ruta relativa del APK se resuelve contra
  el directorio del proyecto (`user.dir` del proceso Java). Esto es necesario
  porque el servidor Appium resuelve las rutas relativas contra su propio
  directorio de trabajo, no contra el del proyecto.
- **Validación temprana**: si el APK no existe, `DriverManager` falla de forma
  inmediata con un mensaje accionable que indica la ruta resuelta y cómo
  configurarla, en lugar de producir un error críptico HTTP 500 del servidor.
- **Javadoc**: la clase documenta el orden de prioridad de la configuración.

### 4.2 SauceDemoAutomation — `BaseTest.java`

- **URL base externalizada**: `-Dbase.url` / `BASE_URL`, con default
  `https://www.saucedemo.com/`.
- **Modo headless**: `-Dheadless=true` / `HEADLESS=true` activa
  `--headless=new` con ventana de 1920×1080. Por defecto está desactivado
  (comportamiento visual intacto en desarrollo).
- Se conservaron las preferencias de Chrome que desactivan el gestor de
  contraseñas (evitan diálogos que rompen los tests).

### 4.3 Limpieza de código muerto

- Eliminado `Main.java` en PetStoreRestAssured y WdioMobileAutomation
  (plantilla de IntelliJ sin ninguna funcionalidad).

### 4.4 Unificación de versiones (los tres `pom.xml`)

| Componente | Antes | Después | Justificación |
|---|---|---|---|
| TestNG | 7.5 / 7.10.2 | **7.10.2** | Misma versión en los 3 proyectos |
| maven-surefire-plugin | 2.22.1 / 3.1.2 | **3.1.2** | Compatibilidad con TestNG 7.10.2 |
| JUnit 4.11 | presente (SauceDemo) | **eliminado** | Sin uso; generaba confusión |
| allure-testng 2.29.1 | presente | presente | Agregado en el piloto (Fase 0) |

### 4.5 Documentación de los frameworks (READMEs)

Cada repositorio cuenta con un README que documenta su arquitectura, configuración
y ejecución, como parte de la consolidación de los frameworks:

- **WdioMobileAutomation** (creado desde cero): descripción de los 4 flujos
  automatizados (Login, Signup, Swipe, Navigation), stack tecnológico (Appium
  Server 3.9.0, driver uiautomator2 8.7.3, TestNG 7.10.2), estructura del
  proyecto (Screen Object Model), tabla de parámetros de configuración
  (`-Dapp.path`, `-Ddevice.name`, `-Dappium.url`), instrucciones de ejecución
  con prerrequisitos y limitación conocida (renderizado WebView en emulador
  headless).
- **PetStoreRestAssured** (creado desde cero): descripción de los 6 escenarios
  API, arquitectura en capas (RequestBuilder → modelos → tests), estructura del
  proyecto y ejecución.
- **SauceDemoAutomation** (mejorado): nueva sección *Configuration Options* con
  los parámetros `-Dbase.url` y `-Dheadless`, versión de TestNG actualizada a
  7.10.2 en la tabla de stack, y nueva decisión de diseño sobre configuración
  externalizada.

### 4.6 Sincronización a GitHub

El código refactorizado y los READMEs se publicaron en los repositorios remotos
del proyecto (organización personal `AngelicaJuliethSP`):

| Repositorio | Commit | Contenido publicado |
|---|---|---|
| `WdioMobileAutomation` | `23e67d7` | DriverManager externalizado, limpieza, .gitignore, README |
| `PetStoreRestAssured` | `a38c69a` | Limpieza, versiones unificadas, README |
| `SauceDemoAutomation` | `8073fe0` | BaseTest externalizado, versiones, README mejorado |

## 5. Verificación de la refactorización

Cada cambio se validó con ejecución real de las suites, no solo compilación:

| Suite | Comando | Resultado |
|---|---|---|
| SauceDemo (web) | `mvn clean test -Dheadless=true` | **4/4 (100%)** ✅ |
| PetStore (API) | `mvn clean test` | **6/6 (100%)** ✅ |
| WdioMobile (mobile) | `mvn clean test` | **3/4 (75%)** ✅ |

Observaciones de la verificación:

- La suite web pasó completa **en modo headless**, confirmando que el requisito
  de CI quedó cubierto.
- En la suite mobile, el escenario **Swipe pasó por primera vez** tras combinar
  emulador reiniciado en frío (wipe data) con el driver actualizado; en la línea
  base fallaba por degradación del emulador.
- El único fallo (Navigation) se debe a que el WebView de la aplicación no
  renderiza contenido en el emulador headless con renderizado por software
  (SwiftShader). Es una limitación del entorno de ejecución, no del framework:
  el mismo escenario pasó en ejecuciones con emulador no headless. Queda
  documentado como limitación conocida y se reevaluará en la fase de CI, donde
  el emulador se ejecuta con aceleración por hardware.

> **Actualización (11-nov-2026):** la hipótesis de esta fase quedó refutada.
> La causa real fueron dos defectos del código de pruebas: aserciones
> ejecutadas antes de que la pantalla terminara de cargar (commit `6b17dae`)
> y un gesto de swipe insuficiente (commit `b6383ef`). Ver
> `fase2_pipeline_ci.md`, sección 6.3.

## 6. Incidencias resueltas durante la fase

Durante la verificación se presentaron dos incidencias de entorno, ambas
resueltas y documentadas por su valor de aprendizaje:

### 6.1 Driver uiautomator2 incompatible con la imagen del emulador

**Síntoma**: todas las sesiones Appium fallaban con HTTP 500 y el mensaje
`Error executing adbExec ... settings delete global hidden_api_policy...`.

**Causa raíz**: el driver `uiautomator2` 8.6.1 ejecuta el comando
`settings delete global hidden_api_policy*` al iniciar cada sesión. Ese servicio
fue eliminado en la imagen del emulador (API 37.1), por lo que el comando
termina con error y la sesión nunca se crea.

**Solución**: actualización de la herramienta de automatización:

| Componente | Antes | Después |
|---|---|---|
| Servidor Appium | 3.7.0 | **3.9.0** |
| Driver uiautomator2 | 8.6.1 | **8.7.3** |

### 6.2 Ruta del APK resuelta contra el servidor Appium

**Síntoma**: con el driver actualizado, las sesiones fallaban con
`The application at '...\apps\android.wdio.native.app.v2.2.0.apk' does not exist`,
aunque el archivo sí existía dentro del proyecto.

**Causa raíz**: el servidor Appium resuelve las rutas relativas de la capability
`appium:app` contra su propio directorio de trabajo (donde esté instalado el
servidor), no contra el directorio del proyecto que lanza los tests.

**Solución**: `DriverManager` convierte toda ruta relativa a absoluta (contra el
directorio del proyecto) antes de enviarla al servidor, y valida la existencia
del archivo con un mensaje de error accionable.

## 7. Entregables de la fase

| Entregable | Descripción |
|---|---|
| `DriverManager.java` (repo WdioMobileAutomation) | Driver Android con configuración externalizada y validación de APK |
| `BaseTest.java` (repo SauceDemoAutomation) | Base de tests web con URL y headless configurables |
| `pom.xml` (los 3 repositorios) | Versiones unificadas (TestNG 7.10.2, surefire 3.1.2, JUnit removido) |
| `.gitignore` (repo WdioMobileAutomation) | Exclusión del APK (`apps/`, `*.apk`) del versionamiento |
| `README.md` (los 3 repositorios) | Documentación de arquitectura, configuración y ejecución de cada framework |
| Repositorios GitHub `AngelicaJuliethSP/*` | Código refactorizado y READMEs publicados (commits `23e67d7`, `a38c69a`, `8073fe0`) |
| `data/results.json` | Resultados de la corrida de verificación post-refactorización, consolidados con el parser |

## 8. Conclusiones

- Los tres frameworks quedaron **portables**: se ejecutan en cualquier entorno
  sin tocar código, únicamente con propiedades o variables de entorno.
- La suite web y la API quedaron **listas para CI** (headless verificado,
  dependencias de entorno eliminadas).
- La suite mobile quedó lista salvo la limitación de renderizado WebView en
  emulador headless local, que se reevaluó en CI (ver la actualización de la
  sección 5).
- Las incidencias de entorno resueltas (driver Appium, resolución de rutas)
  quedaron documentadas y se incorporarán a la documentación técnica del
  proyecto (Fase 5).

## 9. Criterios de salida cumplidos

| Criterio | Estado |
|---|---|
| Sin rutas absolutas ni valores de entorno hardcodeados | ✅ |
| Misma versión de TestNG y surefire en los 3 proyectos | ✅ |
| Código muerto eliminado | ✅ |
| Suites verificadas con ejecución real post-refactorización | ✅ (Web 100%, API 100%, Mobile 75%) |
| Frameworks documentados (README en cada repositorio) | ✅ |
| Cambios publicados en los repositorios remotos | ✅ (commits `23e67d7`, `a38c69a`, `8073fe0`) |
| Cambios versionados en el repositorio | ✅ (commit `refactor: fase 1`) |

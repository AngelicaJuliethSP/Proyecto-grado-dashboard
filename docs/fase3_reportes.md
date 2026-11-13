# Fase 3: Integración de la herramienta de reportes

## 1. Objetivo de la fase

Integrar **Allure Report** a las suites de pruebas para generar, en cada
ejecución del pipeline, un reporte HTML navegable archivado como artefacto,
y consolidar la evidencia comparativa entre las tres suites (Web, API y
Mobile).

## 2. Herramienta seleccionada: Allure Report

Se seleccionó **Allure** frente a la alternativa considerada (ExtentReports)
por las siguientes razones:

| Criterio | Allure | ExtentReports |
|---|---|---|
| Salida estructurada por test | ✅ JSON nativo (`allure-results/`) | ❌ HTML principalmente |
| Ingesta programática al dashboard | ✅ Directa (JSON por test) | ❌ Requiere parsear HTML |
| Reporte HTML navegable | ✅ (Allure CLI) | ✅ |
| Integración con TestNG | ✅ Adaptador oficial (`allure-testng`) | ✅ |
| Historial y tendencias | ✅ (con historial entre corridas) | Parcial |

El criterio decisivo fue el primero: Allure genera **JSON estructurado por
test** (nombre, clase, estado, duración, excepción), que es el insumo directo
de la ingesta al almacén del dashboard. ExtentReports produce principalmente
HTML, mucho más difícil de consumir automáticamente.

## 3. Arquitectura de dos componentes

Conviene distinguir los dos componentes de la solución, que se integraron en
momentos distintos:

| Componente | Función | Integración |
|---|---|---|
| **Allure TestNG adapter** (`allure-testng` 2.29.1) | Se auto-registra como listener de TestNG y escribe un JSON por test en `target/allure-results/` | Integrado en los 3 `pom.xml` durante la fase de consolidación (piloto) |
| **Allure Report CLI** (`allure-commandline`) | Convierte los JSON en el reporte HTML navegable (gráficas, categorías, detalle por test) | Integrado en los 3 workflows en esta fase |

## 4. Implementación en los pipelines

Se agregaron dos pasos al final de cada uno de los tres workflows, ambos con
`if: always()` para que el reporte se genere también cuando la suite falla
(que es precisamente cuando más se necesita):

```yaml
- name: Generate Allure HTML report
  if: always()
  run: |
    npm install -g allure-commandline
    allure generate target/allure-results -o allure-report --clean

- name: Upload Allure HTML report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: allure-report-web   # -api / -mobile según el repo
    path: allure-report/
    retention-days: 7
```

Cada ejecución del pipeline archiva ahora **tres artefactos** de reportes:

| Artefacto | Contenido | Uso |
|---|---|---|
| `surefire-reports-*` | XML nativo de TestNG | Depuración, integración con otras herramientas |
| `allure-results-*` | JSON por test (salida del adaptador) | Ingesta programática al almacén del dashboard |
| `allure-report-*` | Reporte HTML navegable (salida del CLI) | Consulta humana: gráficas, categorías, detalle por test |

## 5. Incidencia y depuración: waits explícitos en la suite web

Durante la verificación de esta fase, el pipeline web presentó **fallos
consistentes** (2 ejecuciones consecutivas con 2 fallos cada una):

| Test | Síntoma | Causa raíz |
|---|---|---|
| `PurchaseTest` (usuario `performance_glitch_user`) | `NoSuchElementException` al leer el mensaje de confirmación | El framework leía el elemento **sin wait**; con ese usuario el sitio tarda en renderizar la confirmación |
| `RemoveCartItemsTest` | Carrito con 0 items en lugar de 3 | Los clicks sobre "Add to cart" se ejecutaban antes de que el inventario (React) terminara de renderizar → clicks perdidos |

La raíz común fue la **ausencia de waits explícitos** en el framework web,
que funcionaba localmente por la velocidad de red pero no bajo las condiciones
de CI (red más lenta, usuario con retardo intencional, renderizado React).

**Corrección aplicada** (punto único de espera en `BasePage`, heredado por
todas las páginas):

- `BasePage`: `WebDriverWait` compartido (10 s) + helper `waitForVisible`.
- `LoginPage.login()`: espera el contenedor del inventario antes de retornar.
- `CheckoutCompletePage.getThankYouMessage()`: espera el mensaje antes de leerlo.
- `CartPage.getCartItemsCount()`: espera el contenedor del carrito (existe
  incluso vacío, por lo que no bloquea el caso "carrito vacío").

Verificación: suite local 4/4 en verde y pipeline de CI en verde tras el fix.

**Lección para el informe:** un framework sin waits explícitos es dependiente
de las condiciones del entorno; el punto único de espera en la clase base
elimina la duplicación y hace el comportamiento uniforme en todas las páginas.

## 6. Evidencia de la fase

| Evidencia | Ubicación |
|---|---|
| Reportes HTML archivados por ejecución | Artefactos `allure-report-web`, `allure-report-api`, `allure-report-mobile` en cada run (7 días) |
| Tabla de comparación de suites | `docs/evidencia_fase3_tabla_comparacion.md` |
| Almacén consolidado | `data/results.json` (10 ejecuciones registradas al cierre de la Fase 3) |
| Fix de waits | Commits de `SauceDemoAutomation` (BasePage, LoginPage, CartPage, CheckoutCompletePage) |

### Tabla de comparación (resumen)

| Suite | Ejecuciones | Tests | Pasados | % Éxito prom. | Duración prom. | Estabilidad |
|---|---|---|---|---|---|---|
| SauceDemoAutomation (Web) | 3 | 12 | 12 | 100.0% | 13.5 s | Estable |
| PetStoreRestAssured (API) | 3 | 18 | 18 | 100.0% | 7.6 s | Estable |
| WdioMobileAutomation (Mobile) | 4 | 28 | 3 | 18.8% | 29.4 s | Intermitente |

La tasa mobile refleja la línea base con el emulador local degradado (fallos
de infraestructura documentados en la línea base) más la corrida de CI al 75%
(Login y Signup estables; Navigation y Swipe como fallas conocidas del
entorno headless).

## 7. Entregables de la fase

| Entregable | Descripción |
|---|---|
| Pasos de Allure en los 3 workflows | Generación + upload del reporte HTML con `if: always()` |
| Artefactos `allure-report-*` | Reporte HTML navegable por cada ejecución (7 días) |
| `docs/evidencia_fase3_tabla_comparacion.md` | Tabla comparativa entre suites con detalle por ejecución |
| Fix de waits en SauceDemo | Punto único de espera en `BasePage` + aplicación en páginas críticas |

## 8. Conclusiones

- Allure quedó integrado de punta a punta: el adaptador genera los JSON por
  test y el CLI los convierte en el reporte HTML, archivado como artefacto en
  cada ejecución del pipeline.
- La elección de Allure sobre ExtentReports se justifica por su salida JSON
  estructurada, que habilita la ingesta programática al dashboard (fase
  siguiente) sin parsear HTML.
- La verificación de la fase destapó una deuda técnica real del framework web
  (ausencia de waits), cuya corrección dejó el framework robusto ante
  variaciones de red y renderizado — hallazgo con valor directo para el
  informe.
- La tabla de comparación consolida la evidencia entre suites y deja
  documentada la situación mobile (dependiente del entorno de ejecución;
  diagnóstico posterior: defectos del código de pruebas, resueltos el 11-nov;
  ver fase2 §6.3).

## 9. Criterios de salida cumplidos

| Criterio | Estado |
|---|---|
| Herramienta de reportes integrada a las suites | ✅ (Allure: adaptador + CLI) |
| Reporte de cada ejecución archivado como artefacto del pipeline | ✅ (`allure-report-*`, 7 días) |
| Reportes archivados (evidencia) | ✅ (3 artefactos por run) |
| Tabla de comparación (evidencia) | ✅ (`docs/evidencia_fase3_tabla_comparacion.md`) |
| Cambios versionados y publicados | ✅ (3 repos + dashboard) |

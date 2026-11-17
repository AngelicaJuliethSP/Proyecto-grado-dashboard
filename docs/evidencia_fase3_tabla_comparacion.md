# Tabla de comparación de suites — Evidencia de reportes

Fuente: `data/results.json` (almacén consolidado de ejecuciones).
Corte: **2026-11-17 20:07 UTC** (15:07 Colombia, 115 registros — corte del
informe: excluye las corridas locales del 11-nov y solo contiene línea base,
verificación de la Fase 1 y ejecuciones de CI).

| Suite | Ejecuciones | Tests | Pasados | Fallados | Skipped | % Éxito prom. | Duración prom. | Estabilidad (últimas 10) |
|---|---|---|---|---|---|---|---|---|
| SauceDemoAutomation | 38 | 152 | 145 | 7 | 0 | 95.4% | 19.4 s | Estable (100% últimas 10) |
| PetStoreRestAssured | 34 | 204 | 204 | 0 | 0 | 100.0% | 3.9 s | Estable (100% últimas 10) |
| WdioMobileAutomation | 43 | 168 | 122 | 34 | 12 | 72.5% | 99.2 s | Estable (100% últimas 10) |

> Nota: los promedios de WdioMobile arrastran los fallos previos a las
> correcciones de la suite móvil: aserciones prematuras y gesto de swipe
> insuficiente (corregidos el 11-nov en los commits 6b17dae y b6383ef) y la
> espera que faltaba en `WebScreen` (fallo del 14-nov, corregido en 1e21b8b).
> Desde 1e21b8b, las 4 pruebas pasaron en las 11 ejecuciones de CI
> registradas hasta el corte.

## Detalle por ejecución

| Suite | Fecha (UTC) | Tests | Pasados | Fallados | Skipped | % Éxito | Duración |
|---|---|---|---|---|---|---|---|
| SauceDemoAutomation | 2026-11-06T16:24:50 | 4 | 4 | 0 | 0 | 100.0% | 14.0 s |
| SauceDemoAutomation | 2026-11-06T16:25:47 | 4 | 4 | 0 | 0 | 100.0% | 14.2 s |
| SauceDemoAutomation | 2026-11-06T16:26:39 | 4 | 4 | 0 | 0 | 100.0% | 12.4 s |
| PetStoreRestAssured | 2026-11-06T16:27:08 | 6 | 6 | 0 | 0 | 100.0% | 7.8 s |
| PetStoreRestAssured | 2026-11-06T16:27:33 | 6 | 6 | 0 | 0 | 100.0% | 7.1 s |
| PetStoreRestAssured | 2026-11-06T16:28:01 | 6 | 6 | 0 | 0 | 100.0% | 7.7 s |
| WdioMobileAutomation | 2026-11-06T16:28:36 | 4 | 0 | 0 | 4 | 0.0% | 0.0 s |
| WdioMobileAutomation | 2026-11-06T16:29:09 | 4 | 0 | 0 | 4 | 0.0% | 0.0 s |
| WdioMobileAutomation | 2026-11-06T16:29:49 | 4 | 0 | 0 | 4 | 0.0% | 0.0 s |
| WdioMobileAutomation | 2026-11-07T00:45:46 | 4 | 3 | 1 | 0 | 75.0% | 117.8 s |
| SauceDemoAutomation | 2026-11-07T01:27:14 | 4 | 4 | 0 | 0 | 100.0% | 12.9 s |
| PetStoreRestAssured | 2026-11-07T01:27:18 | 6 | 6 | 0 | 0 | 100.0% | 2.5 s |
| WdioMobileAutomation | 2026-11-07T01:32:12 | 4 | 2 | 2 | 0 | 50.0% | 60.9 s |
| WdioMobileAutomation | 2026-11-07T01:43:15 | 3 | 0 | 3 | 0 | 0.0% | 74.5 s |
| WdioMobileAutomation | 2026-11-07T01:57:50 | 3 | 2 | 1 | 0 | 66.7% | 58.5 s |
| WdioMobileAutomation | 2026-11-07T02:07:47 | 2 | 2 | 0 | 0 | 100.0% | 63.2 s |
| WdioMobileAutomation | 2026-11-08T02:00:34 | 4 | 3 | 1 | 0 | 75.0% | 116.6 s |
| SauceDemoAutomation | 2026-11-08T15:18:16 | 4 | 2 | 2 | 0 | 50.0% | 18.3 s |
| PetStoreRestAssured | 2026-11-08T15:18:20 | 6 | 6 | 0 | 0 | 100.0% | 2.9 s |
| SauceDemoAutomation | 2026-11-08T17:24:25 | 4 | 2 | 2 | 0 | 50.0% | 12.8 s |
| SauceDemoAutomation | 2026-11-08T17:40:46 | 4 | 4 | 0 | 0 | 100.0% | 13.5 s |
| SauceDemoAutomation | 2026-11-08T18:20:22 | 4 | 4 | 0 | 0 | 100.0% | 13.8 s |
| PetStoreRestAssured | 2026-11-08T18:20:26 | 6 | 6 | 0 | 0 | 100.0% | 3.5 s |
| WdioMobileAutomation | 2026-11-08T18:20:31 | 4 | 2 | 2 | 0 | 50.0% | 120.9 s |
| SauceDemoAutomation | 2026-11-08T18:39:19 | 4 | 4 | 0 | 0 | 100.0% | 13.5 s |
| PetStoreRestAssured | 2026-11-08T18:39:23 | 6 | 6 | 0 | 0 | 100.0% | 3.8 s |
| WdioMobileAutomation | 2026-11-08T18:39:27 | 4 | 2 | 2 | 0 | 50.0% | 120.7 s |
| SauceDemoAutomation | 2026-11-08T18:49:11 | 4 | 4 | 0 | 0 | 100.0% | 19.7 s |
| PetStoreRestAssured | 2026-11-08T18:49:15 | 6 | 6 | 0 | 0 | 100.0% | 3.3 s |
| WdioMobileAutomation | 2026-11-08T18:49:19 | 4 | 2 | 2 | 0 | 50.0% | 102.6 s |
| SauceDemoAutomation | 2026-11-08T18:58:23 | 4 | 3 | 1 | 0 | 75.0% | 21.0 s |
| WdioMobileAutomation | 2026-11-08T18:58:27 | 4 | 2 | 2 | 0 | 50.0% | 126.9 s |
| PetStoreRestAssured | 2026-11-08T18:58:27 | 6 | 6 | 0 | 0 | 100.0% | 2.8 s |
| SauceDemoAutomation | 2026-11-08T22:03:02 | 4 | 4 | 0 | 0 | 100.0% | 22.5 s |
| WdioMobileAutomation | 2026-11-08T22:18:13 | 4 | 2 | 2 | 0 | 50.0% | 81.4 s |
| PetStoreRestAssured | 2026-11-08T22:18:14 | 6 | 6 | 0 | 0 | 100.0% | 3.2 s |
| WdioMobileAutomation | 2026-11-09T01:14:16 | 4 | 3 | 1 | 0 | 75.0% | 126.5 s |
| PetStoreRestAssured | 2026-11-09T01:14:20 | 6 | 6 | 0 | 0 | 100.0% | 3.2 s |
| WdioMobileAutomation | 2026-11-09T15:18:13 | 4 | 2 | 2 | 0 | 50.0% | 145.8 s |
| SauceDemoAutomation | 2026-11-09T15:47:15 | 4 | 4 | 0 | 0 | 100.0% | 19.3 s |
| PetStoreRestAssured | 2026-11-09T15:47:26 | 6 | 6 | 0 | 0 | 100.0% | 3.5 s |
| WdioMobileAutomation | 2026-11-09T15:47:39 | 4 | 2 | 2 | 0 | 50.0% | 141.2 s |
| SauceDemoAutomation | 2026-11-09T15:50:55 | 4 | 2 | 2 | 0 | 50.0% | 13.3 s |
| SauceDemoAutomation | 2026-11-09T16:09:45 | 4 | 4 | 0 | 0 | 100.0% | 19.9 s |
| PetStoreRestAssured | 2026-11-09T16:59:51 | 6 | 6 | 0 | 0 | 100.0% | 3.1 s |
| SauceDemoAutomation | 2026-11-09T17:30:11 | 4 | 4 | 0 | 0 | 100.0% | 19.5 s |
| PetStoreRestAssured | 2026-11-09T17:30:15 | 6 | 6 | 0 | 0 | 100.0% | 2.5 s |
| WdioMobileAutomation | 2026-11-09T17:30:25 | 4 | 2 | 2 | 0 | 50.0% | 136.6 s |
| WdioMobileAutomation | 2026-11-09T17:32:07 | 4 | 3 | 1 | 0 | 75.0% | 161.9 s |
| SauceDemoAutomation | 2026-11-09T17:57:17 | 4 | 4 | 0 | 0 | 100.0% | 24.9 s |
| SauceDemoAutomation | 2026-11-09T17:58:40 | 4 | 4 | 0 | 0 | 100.0% | 13.7 s |
| PetStoreRestAssured | 2026-11-09T18:01:56 | 6 | 6 | 0 | 0 | 100.0% | 3.5 s |
| PetStoreRestAssured | 2026-11-09T18:03:00 | 6 | 6 | 0 | 0 | 100.0% | 3.9 s |
| WdioMobileAutomation | 2026-11-09T18:06:48 | 4 | 3 | 1 | 0 | 75.0% | 159.9 s |
| SauceDemoAutomation | 2026-11-09T19:46:51 | 4 | 4 | 0 | 0 | 100.0% | 13.3 s |
| PetStoreRestAssured | 2026-11-09T19:47:03 | 6 | 6 | 0 | 0 | 100.0% | 4.8 s |
| WdioMobileAutomation | 2026-11-09T19:47:28 | 4 | 2 | 2 | 0 | 50.0% | 131.6 s |
| SauceDemoAutomation | 2026-11-09T20:14:23 | 4 | 4 | 0 | 0 | 100.0% | 13.7 s |
| WdioMobileAutomation | 2026-11-10T13:54:25 | 4 | 2 | 2 | 0 | 50.0% | 131.0 s |
| SauceDemoAutomation | 2026-11-10T13:59:32 | 4 | 4 | 0 | 0 | 100.0% | 28.7 s |
| PetStoreRestAssured | 2026-11-10T14:02:54 | 6 | 6 | 0 | 0 | 100.0% | 4.7 s |
| WdioMobileAutomation | 2026-11-11T13:04:34 | 4 | 2 | 2 | 0 | 50.0% | 93.5 s |
| SauceDemoAutomation | 2026-11-11T13:15:42 | 4 | 4 | 0 | 0 | 100.0% | 18.7 s |
| PetStoreRestAssured | 2026-11-11T13:20:48 | 6 | 6 | 0 | 0 | 100.0% | 4.6 s |
| WdioMobileAutomation | 2026-11-12T01:32:17 | 4 | 4 | 0 | 0 | 100.0% | 202.7 s |
| PetStoreRestAssured | 2026-11-12T01:46:40 | 6 | 6 | 0 | 0 | 100.0% | 2.9 s |
| SauceDemoAutomation | 2026-11-12T01:46:51 | 4 | 4 | 0 | 0 | 100.0% | 20.0 s |
| WdioMobileAutomation | 2026-11-12T01:52:29 | 4 | 4 | 0 | 0 | 100.0% | 199.4 s |
| WdioMobileAutomation | 2026-11-12T03:37:35 | 4 | 4 | 0 | 0 | 100.0% | 151.3 s |
| WdioMobileAutomation | 2026-11-12T14:08:34 | 4 | 4 | 0 | 0 | 100.0% | 178.9 s |
| SauceDemoAutomation | 2026-11-12T14:20:16 | 4 | 4 | 0 | 0 | 100.0% | 32.9 s |
| PetStoreRestAssured | 2026-11-12T14:24:57 | 6 | 6 | 0 | 0 | 100.0% | 5.7 s |
| WdioMobileAutomation | 2026-11-12T23:43:07 | 4 | 4 | 0 | 0 | 100.0% | 101.0 s |
| SauceDemoAutomation | 2026-11-12T23:55:44 | 4 | 4 | 0 | 0 | 100.0% | 24.7 s |
| PetStoreRestAssured | 2026-11-12T23:55:49 | 6 | 6 | 0 | 0 | 100.0% | 3.2 s |
| WdioMobileAutomation | 2026-11-13T00:05:46 | 4 | 4 | 0 | 0 | 100.0% | 101.7 s |
| SauceDemoAutomation | 2026-11-13T00:17:59 | 4 | 4 | 0 | 0 | 100.0% | 20.3 s |
| WdioMobileAutomation | 2026-11-13T00:18:08 | 4 | 4 | 0 | 0 | 100.0% | 88.4 s |
| WdioMobileAutomation | 2026-11-13T13:31:03 | 4 | 4 | 0 | 0 | 100.0% | 69.3 s |
| SauceDemoAutomation | 2026-11-13T13:41:09 | 4 | 4 | 0 | 0 | 100.0% | 48.2 s |
| PetStoreRestAssured | 2026-11-13T13:43:41 | 6 | 6 | 0 | 0 | 100.0% | 2.0 s |
| WdioMobileAutomation | 2026-11-14T12:37:23 | 4 | 3 | 1 | 0 | 75.0% | 82.4 s |
| SauceDemoAutomation | 2026-11-14T12:45:23 | 4 | 4 | 0 | 0 | 100.0% | 36.9 s |
| PetStoreRestAssured | 2026-11-14T12:48:13 | 6 | 6 | 0 | 0 | 100.0% | 1.6 s |
| WdioMobileAutomation | 2026-11-14T20:11:59 | 4 | 4 | 0 | 0 | 100.0% | 72.1 s |
| PetStoreRestAssured | 2026-11-14T20:17:26 | 6 | 6 | 0 | 0 | 100.0% | 3.4 s |
| SauceDemoAutomation | 2026-11-14T20:17:43 | 4 | 4 | 0 | 0 | 100.0% | 13.1 s |
| WdioMobileAutomation | 2026-11-14T20:20:50 | 4 | 4 | 0 | 0 | 100.0% | 79.2 s |
| PetStoreRestAssured | 2026-11-14T20:47:19 | 6 | 6 | 0 | 0 | 100.0% | 4.2 s |
| SauceDemoAutomation | 2026-11-14T20:47:35 | 4 | 4 | 0 | 0 | 100.0% | 21.4 s |
| WdioMobileAutomation | 2026-11-14T20:50:47 | 4 | 4 | 0 | 0 | 100.0% | 78.4 s |
| WdioMobileAutomation | 2026-11-15T13:02:35 | 4 | 4 | 0 | 0 | 100.0% | 78.3 s |
| SauceDemoAutomation | 2026-11-15T13:12:13 | 4 | 4 | 0 | 0 | 100.0% | 12.9 s |
| PetStoreRestAssured | 2026-11-15T13:15:02 | 6 | 6 | 0 | 0 | 100.0% | 3.2 s |
| WdioMobileAutomation | 2026-11-16T14:06:04 | 4 | 4 | 0 | 0 | 100.0% | 69.4 s |
| SauceDemoAutomation | 2026-11-16T14:20:59 | 4 | 4 | 0 | 0 | 100.0% | 21.4 s |
| PetStoreRestAssured | 2026-11-16T14:26:27 | 6 | 6 | 0 | 0 | 100.0% | 3.7 s |
| SauceDemoAutomation | 2026-11-16T21:42:20 | 4 | 4 | 0 | 0 | 100.0% | 19.6 s |
| PetStoreRestAssured | 2026-11-16T21:43:03 | 6 | 6 | 0 | 0 | 100.0% | 4.5 s |
| WdioMobileAutomation | 2026-11-16T21:44:27 | 4 | 4 | 0 | 0 | 100.0% | 79.9 s |
| SauceDemoAutomation | 2026-11-17T01:08:19 | 4 | 4 | 0 | 0 | 100.0% | 14.7 s |
| PetStoreRestAssured | 2026-11-17T01:08:37 | 6 | 6 | 0 | 0 | 100.0% | 3.2 s |
| WdioMobileAutomation | 2026-11-17T01:11:18 | 4 | 4 | 0 | 0 | 100.0% | 82.1 s |
| PetStoreRestAssured | 2026-11-17T02:16:54 | 6 | 6 | 0 | 0 | 100.0% | 3.5 s |
| SauceDemoAutomation | 2026-11-17T02:17:05 | 4 | 4 | 0 | 0 | 100.0% | 19.2 s |
| WdioMobileAutomation | 2026-11-17T02:20:00 | 4 | 4 | 0 | 0 | 100.0% | 77.4 s |
| WdioMobileAutomation | 2026-11-17T15:00:20 | 4 | 4 | 0 | 0 | 100.0% | 76.4 s |
| SauceDemoAutomation | 2026-11-17T15:14:01 | 4 | 4 | 0 | 0 | 100.0% | 24.9 s |
| PetStoreRestAssured | 2026-11-17T15:18:29 | 6 | 6 | 0 | 0 | 100.0% | 3.0 s |
| PetStoreRestAssured | 2026-11-17T16:45:35 | 6 | 6 | 0 | 0 | 100.0% | 3.7 s |
| SauceDemoAutomation | 2026-11-17T16:45:51 | 4 | 4 | 0 | 0 | 100.0% | 19.0 s |
| WdioMobileAutomation | 2026-11-17T16:49:06 | 4 | 4 | 0 | 0 | 100.0% | 62.5 s |
| PetStoreRestAssured | 2026-11-17T20:05:01 | 6 | 6 | 0 | 0 | 100.0% | 4.9 s |
| SauceDemoAutomation | 2026-11-17T20:05:16 | 4 | 4 | 0 | 0 | 100.0% | 16.2 s |
| WdioMobileAutomation | 2026-11-17T20:07:40 | 4 | 4 | 0 | 0 | 100.0% | 64.1 s |

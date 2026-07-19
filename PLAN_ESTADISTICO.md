# Implementación De Análisis Estadístico Inferencial

## Estado

La auditoría estadística fue rediseñada para utilizar una cohorte productiva limpia y observaciones identificables. Los datos sintéticos antiguos se eliminaron de Supabase. La migración `query8_metricas_inferenciales.sql` marca cualquier telemetría anterior como `legacy`, que queda fuera del análisis académico.

## Preguntas Principales

1. ¿La latencia media end-to-end de un flujo cambió entre el Periodo A y el Periodo B?
2. ¿La proporción de ejecuciones exitosas y fallidas cambió entre ambos periodos?

Las comparaciones se realizan sobre un único endpoint seleccionado. No se mezclan flujos con cargas de trabajo diferentes.

## Métodos Implementados

### Latencia

- Prueba t de Welch bilateral para muestras independientes.
- Población: ejecuciones `production`, terminales y exitosas.
- Medida: `end_to_end_latency_seconds`.
- Reporte: n, media, DE, mediana, RIC, diferencia B-A, IC 95%, t, grados de libertad, p-value y g de Hedges.
- Casos sin datos o sin varianza: estado estructurado sin fabricar `p=1`.

### Resultados

- Tabla 2x2 de éxito/fallo por periodo.
- Fallo terminal: `error` o `timeout`.
- `pending` y `cancelled` se excluyen.
- Chi-cuadrado de Pearson sin corrección de Yates cuando todas las frecuencias esperadas son al menos 5.
- Fisher exacta bilateral cuando alguna frecuencia esperada es menor que 5.
- Reporte: conteos, tasas, esperados, estadístico, grados de libertad, p-value, odds ratio, IC 95%, diferencia de riesgos y V de Cramér cuando corresponde.

## Interpretación

- Umbral primario: `alpha = 0.05`.
- Las pruebas son bilaterales.
- Un resultado no significativo se interpreta como falta de evidencia suficiente de diferencia.
- No se afirma estabilidad, equivalencia ni causalidad a partir de `p >= 0.05`.
- Mejora significa menor latencia o mayor tasa de éxito en B; empeoramiento significa lo contrario.

## Integridad De Datos

- Una fila por invocación mediante `invocation_id`.
- Procesos asíncronos vinculados mediante `correlation_id`.
- Estados internos canónicos y un único resultado terminal.
- Tiempos UTC medidos con reloj monotónico durante la ejecución.
- Latencia de transporte separada de duración end-to-end.
- Filtrado en Supabase, orden determinista y paginación completa.
- Separación obligatoria entre `production`, `demo`, `test` y `legacy`.

## Frontend

- Selector obligatorio de endpoint.
- Validación de periodos ordenados y no superpuestos.
- Resultados tipados y estados `ok`, `insufficient_data`, `not_estimable` e `invalid_data`.
- Tabla accesible de descriptivos e inferencia.
- Gráfico categórico apilado al 100%.
- Colores acompañados de etiquetas textuales de mejora, empeoramiento o ausencia de evidencia.
- Descarga JSON y hashes de los conjuntos analizados.

## Demostración

`seed_metricas_estadisticas.sql` contiene 300 filas deterministas con fechas fijas y `data_source='demo'`. Sirve para validar la interfaz, nunca para sustentar resultados del artículo.

## Verificación

- Pruebas unitarias de Welch, Chi-cuadrado, Fisher y casos degenerados.
- Pruebas de una fila por invocación y finalización asíncrona.
- Prueba de paginación por encima del límite del servidor.
- Build y lint dirigido del frontend.
- Exportación CSV con manifiesto y SHA-256 para reproducción externa.

La metodología publicable y los criterios previos a congelar la muestra se detallan en `METODOLOGIA_ESTADISTICA.md`.

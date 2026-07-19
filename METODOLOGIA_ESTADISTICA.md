# Protocolo De Auditoría Estadística De n8n

## 1. Objetivo

Evaluar cambios temporales en el rendimiento de un mismo flujo automatizado mediante dos resultados primarios: latencia end-to-end y proporción de ejecuciones terminales exitosas.

## 2. Unidad De Análisis

La unidad es una invocación única identificada por `invocation_id`. Un reintento es una nueva invocación con `attempt_number` propio. Una invocación solo puede aportar un resultado terminal.

Los procesos asíncronos permanecen `pending` hasta recibir callback. El callback finaliza la fila correlacionada por `job_id`. Las filas `pending` y `cancelled` no participan en las pruebas principales.

## 3. Población Y Exclusiones

Se incluyen únicamente filas que cumplan simultáneamente:

- `data_source = 'production'`.
- Endpoint igual al flujo seleccionado.
- Inicio dentro del periodo UTC solicitado.
- `is_terminal = true`.
- `outcome` reconocido.

Welch añade los criterios `outcome = 'success'` y latencia end-to-end positiva y finita. Se excluyen datos `legacy`, `demo`, `test`, pendientes, cancelados, estados desconocidos y latencias ausentes o inválidas. La API informa los conteos excluidos.

## 4. Periodos

Los periodos son fechas calendario UTC inclusivas transformadas a intervalos semiabiertos `[inicio, fin + 1 día)`. No pueden invertirse, coincidir ni superponerse. El Periodo A debe representar la referencia y B el periodo posterior definido en el protocolo del artículo.

## 5. Hipótesis De Latencia

- H0: la media de latencia end-to-end es igual en A y B.
- H1: las medias son diferentes.

Se usa una prueba t de Welch bilateral porque no se presupone igualdad de varianzas. Se reporta la diferencia `media_B - media_A`; un valor negativo favorece a B.

El reporte incluye n, media, desviación estándar, mediana, rango intercuartílico, estadístico t, grados de libertad de Welch, p-value, diferencia de medias, IC 95% y g de Hedges. Mediana y RIC permiten describir la asimetría habitual de latencias, pero no sustituyen la prueba primaria.

## 6. Hipótesis De Resultados

- H0: la proporción de éxito es independiente del periodo.
- H1: la proporción de éxito difiere entre periodos.

`success` es éxito; `error` y `timeout` son fallos. Se construye una tabla 2x2. Si todas las frecuencias esperadas son al menos 5 se usa Chi-cuadrado de Pearson bilateral sin corrección de Yates. Si alguna es menor que 5 se usa Fisher exacta bilateral. Si solo existe una categoría de resultado, la comparación se declara no estimable.

Se reportan conteos, tasas, esperados, estadístico, grados de libertad, p-value, odds ratio de B frente a A, IC 95%, diferencia de riesgos `B-A` y V de Cramér para Pearson. Cuando existe una celda observada en cero, el odds ratio y su intervalo utilizan la corrección de Haldane-Anscombe de 0,5 y el reporte lo identifica explícitamente.

## 7. Significancia E Interpretación

El nivel de significancia es 0.05. Las dos preguntas son resultados primarios distintos y deben declararse antes de examinar los datos. Si el artículo realiza comparaciones adicionales exploratorias, deben etiquetarse como tales y considerar ajuste de multiplicidad, por ejemplo Holm.

`p < 0.05` indica evidencia contra H0, no importancia práctica ni causalidad. `p >= 0.05` no demuestra igualdad o estabilidad. Una afirmación formal de equivalencia requeriría definir un margen relevante e implementar un análisis TOST separado.

## 8. Tamaño Muestral

Antes de recolectar la muestra definitiva se debe fijar:

- Diferencia mínima relevante de latencia en segundos.
- Cambio mínimo relevante en tasa de éxito.
- Potencia objetivo, recomendada al menos 80%.
- Nivel alfa y asignación esperada por periodo.

El cálculo de potencia debe conservarse como anexo del artículo. El sistema solo exige el mínimo matemático y muestra `insufficient_data`; no inventa un umbral universal sin conocer el efecto relevante del estudio.

## 9. Reproducibilidad

Antes de publicar:

1. Fijar endpoint, periodos, exclusiones y versión del workflow.
2. Detener cambios de instrumentación durante la ventana analítica.
3. Exportar el CSV con `scripts.export_metrics_dataset`.
4. Conservar el manifiesto y hash SHA-256.
5. Descargar el resultado JSON del panel.
6. Registrar commit, Python, NumPy y SciPy utilizados.
7. Recalcular los resultados con un script independiente o software estadístico externo.

Las versiones reproducibles del backend están en `backend/requirements.lock.txt`.

## 10. Datos Sintéticos

El seed determinista solo valida cálculos, estados y visualizaciones. Sus resultados no constituyen observaciones empíricas y no se deben citar como rendimiento real del sistema.

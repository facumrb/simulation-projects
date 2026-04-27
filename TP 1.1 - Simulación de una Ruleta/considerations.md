# Lo que **deberías analizar** es esto:

**Parámetros Del Experimento**
- Cantidad de tiradas por corrida.
- Cantidad de corridas independientes.
- Número elegido para seguir la frecuencia relativa.
- Semilla usada, si aplicaste `--seed`, para garantizar reproducibilidad.
- Archivo de salida generado con los gráficos.

**Resultados Numéricos Finales**
- Frecuencia relativa final promedio entre corridas.
- Promedio final de las tiradas entre corridas.
- Desvío estándar final promedio entre corridas.
- Varianza final promedio entre corridas.
- Diferencia entre cada valor empírico y su valor teórico.

**Comparación Contra Valores Teóricos**
- Frecuencia relativa vs. `1/37 ≈ 0.0270`.
- Promedio vs. `18`.
- Varianza vs. `114`.
- Desvío estándar vs. `sqrt(114) ≈ 10.68`.
- Magnitud del error absoluto y, si querés más rigor, error relativo porcentual.

**Convergencia**
- Si la frecuencia relativa acumulada tiende a estabilizarse cerca de `1/37`.
- Si el promedio acumulado converge hacia `18`.
- Si la varianza y el desvío acumulados se aproximan a `114` y `10.68`.
- Desde qué cantidad de tiradas empieza a verse una estabilización razonable.
- Si con más tiradas la convergencia mejora claramente.

**Variabilidad Entre Corridas**
- Qué tan dispersas son las corridas individuales.
- Si la banda percentil `10–90` se achica al aumentar las tiradas.
- Cuánto difieren entre sí las corridas al inicio y cuánto al final.
- Si todavía hay corridas alejadas de la referencia teórica pese a tener muchas observaciones.

**Lectura De Los Gráficos**
- Qué muestran las líneas finas: corridas individuales.
- Qué muestra la línea gruesa: promedio entre corridas por tirada.
- Qué muestra la banda sombreada: dispersión entre corridas.
- Qué indica la línea roja punteada: valor teórico de referencia.
- En qué métricas la convergencia es más rápida y en cuáles más lenta.

**Comparación Entre Experimentos**
- Diferencias entre correr `100` tiradas y `1000` tiradas.
- Qué experimento produce métricas más estables.
- En cuál hay menor dispersión entre corridas.
- En cuál el promedio entre corridas queda más cerca del valor teórico.
- Si el aumento del tamaño muestral mejora la calidad visual y estadística del resultado.

**Interpretación Estadística**
- Si los resultados observados son compatibles con una ruleta justa.
- Si las diferencias respecto de la teoría parecen atribuibles al azar muestral.
- Cómo se evidencia la ley de los grandes números.
- Qué métricas son más sensibles a muestras pequeñas.
- Qué conclusiones son sólidas y cuáles deben expresarse con cautela.

**Discusión Metodológica**
- Que el análisis de frecuencia relativa se hace sobre un solo número.
- Que solo se comparan ciertos tamaños muestrales concretos.
- Que el modelo supone una ruleta ideal sin sesgos.
- Que las conclusiones valen dentro de ese diseño experimental.
- Qué extensiones futuras podrían mejorar el estudio.

**Qué Debería Quedar Escrito En `main.tex`**
- Configuración exacta del experimento.
- Valores empíricos finales reportados por el script.
- Comparación explícita con teoría.
- Interpretación de convergencia y dispersión.
- Limitaciones metodológicas.
- Conclusión final apoyada en los gráficos y en el resumen numérico.

Si querés, el siguiente paso te lo puedo dejar todavía más práctico: te armo una **checklist lista para pegar en `main.tex`** como subsección “Aspectos analizados tras la ejecución de la simulación”.
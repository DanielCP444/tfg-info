# TFG — Generación automatizada de informes climatológicos mediante LLM

Trabajo de Fin de Grado (Ingeniería Informática, UCM) que diseña, desarrolla y evalúa un sistema para producir informes climatológicos en lenguaje natural a partir de datos históricos de la AEMET, combinando un pipeline de ingeniería de datos con modelos de lenguaje de gran tamaño (LLM).

## Descripción

El sistema extrae y limpia datos climáticos diarios de la estación de Madrid Retiro (1996–2025), realiza un análisis exploratorio que sirve como control de calidad de la fuente, y diseña un conjunto de instrucciones (*prompts*) que permite a un LLM analizar la matriz de datos en bruto y redactar un informe climatológico completo: clasificación climática, tendencias de temperatura y olas de calor, evolución de la aridez, consecuencias prácticas y conclusiones, junto con las gráficas correspondientes.

Como parte central del trabajo, se evalúa comparativamente el comportamiento de tres LLM de propósito general (Gemini 3.5 Flash, GPT-5.5 Instant y Claude Sonnet 5) ante las mismas instrucciones, auditando su fidelidad a los datos y la relevancia de sus respuestas.

## Estructura del repositorio

### Pipeline ETL

- Extracción de datos diarios mediante la API OpenData de la AEMET (arquitectura HATEOAS, doble petición HTTP)
- Gestión de las restricciones de la API (bloques de 15 días, retroceso exponencial ante errores 429)
- Limpieza: interpolación lineal en variables continuas, tratamiento específico de la precipitación
- Enriquecimiento con evapotranspiración potencial (método de Hargreaves-Samani)

### Análisis Exploratorio de Datos

- Generación de gráficas para validar la fuente de datos
- Test de Mann-Kendall y pendiente de Sen para detección de tendencias

### Diseño de prompts

- *Framework* TAREA como estructura base de las instrucciones
- *Few-shot* para orientar el tono narrativo sin condicionar el contenido
- El LLM recibe la matriz de datos completa, realizando él mismo el análisis

### Generación de informes
- En llm.py se encuentra el código que utilizaríamos para generar automáticamente los informes en pdf interactuando con las API de los LLM
- No se utilizó finalmente en el trabajo pues no se pueden utilizar las API de manera gratuita

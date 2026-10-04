## Why

En una prueba real, "qué gacetas existen hoy" no preguntó al usuario por sus temas de interés (las instrucciones decían explícitamente que no hacía falta en consultas por fecha) y la respuesta abrevió los nombres: faltaban el nombre completo de la gaceta ("Gaceta Oficial No. 92 Extraordinaria de 2026") y el título completo de cada norma con su enlace, por lo que el usuario no podía ubicarse.

## What Changes

- El agente SHALL preguntar por el tema de interés antes de CUALQUIER búsqueda (por fecha o por contenido); si el usuario no tiene tema, se usan los temas guardados.
- `list_ediciones` acepta `topics_` y marca qué normas de las ediciones coinciden con los temas (cruzando con la búsqueda avanzada del año del periodo), incluyendo su resumen.
- Cada gaceta devuelve `nombre_completo` (p. ej. "Gaceta Oficial No. 92 Extraordinaria de 2026").
- Las instrucciones exigen presentar el nombre completo de la gaceta y el título completo, enlace y PDF de cada norma, sin abreviar.

## Capabilities

### Modified Capabilities
- `temas-de-interes`: la confirmación de tema aplica también a consultas por fecha.
- `ediciones-por-fecha`: marcado de normas por tema y nombre completo de la gaceta.
- `busqueda-gacetas`: nombre completo también en las gacetas devueltas por `search_gacetas` y `search_gacetas_historicas`.

## Impact

Cambia las instrucciones del servidor y la forma de la respuesta (campos nuevos, compatibles). `list_ediciones` con temas hace más peticiones al sitio (hasta 5 páginas por tema).

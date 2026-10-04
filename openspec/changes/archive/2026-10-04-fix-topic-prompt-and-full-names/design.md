## Context

El flujo original excluía las consultas por fecha de la pregunta de temas, y los títulos de `normas` en las ediciones no traen resumen, por lo que no se puede filtrar por tema solo con el listado de la edición.

## Decisions

- **Preguntar siempre**: se elimina la excepción para fechas en las `instructions`; la pregunta la hace el agente (no hay forma portable de que el servidor interrogue al usuario).
- **Cruce por búsqueda avanzada**: para marcar normas por tema en `list_ediciones` se ejecuta `getdata` por tema con `anno` del periodo (hasta 5 páginas de 10) y se cruza por URL con las normas de las ediciones. Evita descargar la página de cada norma. Límite conocido: normas fuera de las primeras 50 coincidencias del tema en ese año no se marcan.
- **`nombre_completo`** se calcula en los parsers a partir de número, tipo y año de la fecha (o del slug si no hay fecha).

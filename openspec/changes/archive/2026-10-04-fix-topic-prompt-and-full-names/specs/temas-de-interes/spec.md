## MODIFIED Requirements

### Requirement: Confirmación previa de tema
Las `instructions` del servidor y las descripciones de las herramientas SHALL ordenar al agente preguntar al usuario, antes de CUALQUIER búsqueda (por fecha o por contenido), si desea un tema específico; si no lo desea, se usan los temas guardados.

#### Scenario: Usuario sin tema
- **WHEN** el usuario responde que no tiene un tema específico
- **THEN** se usan los temas guardados: `search_normas` hace una búsqueda por tema con resultados deduplicados y etiquetados, y `list_ediciones` marca las normas que coinciden con ellos

#### Scenario: Consulta por fecha
- **WHEN** la consulta es por fecha ("qué gacetas existen hoy")
- **THEN** el agente pregunta primero por el tema y luego llama a `list_ediciones` con los temas elegidos

## ADDED Requirements

### Requirement: Listado de ediciones por periodo
El servidor SHALL exponer `list_ediciones` que consulta `POST /es/getedicionesgaceta` (página `/es/ediciones-del-mes`) con `mes` (0-11, base cero; -1 = todos), `anno` (0 = todos), `from`, `page` y `buscar=1`.

#### Scenario: Gacetas de hoy
- **WHEN** el usuario pregunta "¿qué gacetas existen hoy?"
- **THEN** se consulta el mes y año actuales y se filtran las ediciones cuya fecha es la de hoy; si no hay ninguna se devuelve el mensaje "No hay gacetas publicadas en ese periodo" y se ofrece la última edición disponible

#### Scenario: Mes y año en lenguaje natural
- **WHEN** el usuario pide "octubre de 2025"
- **THEN** se convierte a `mes=9`, `anno=2025`

### Requirement: Contenido de cada edición
Cada edición devuelta SHALL incluir tipo, número, fecha, URL de la gaceta, URL del PDF y la lista de normas que contiene.

#### Scenario: Edición con normas
- **WHEN** una edición contiene normas
- **THEN** cada norma aparece con título y URL absoluta

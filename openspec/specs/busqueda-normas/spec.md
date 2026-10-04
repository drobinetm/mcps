# busqueda-normas Specification

## Purpose
TBD - created by archiving change add-gaceta-mcp-server. Update Purpose after archive.

## Requirements

### Requirement: Búsqueda avanzada de normas
El servidor SHALL exponer la herramienta `search_normas` que consulta `POST /es/getdata` con `buscar=2`, aceptando texto, tipo de norma, estado, organismo, año, número, identificador, palabras clave y página.

#### Scenario: Búsqueda por texto
- **WHEN** el usuario pide "gacetas que hablan sobre el contrato de trabajo en las mipymes"
- **THEN** se invoca `search_normas` con el texto y se devuelven título, tipo, URL absoluta y resumen de cada norma

#### Scenario: Sin filtros
- **WHEN** no se proporciona ningún filtro ni tema
- **THEN** se usan los temas de interés guardados; la herramienta nunca envía una búsqueda totalmente vacía al sitio

#### Scenario: Paginación
- **WHEN** hay más resultados
- **THEN** la respuesta incluye `has_more` y se puede solicitar la siguiente `page`

### Requirement: Tolerancia a frases largas
Como el sitio busca la frase literal, si una frase de varias palabras no produce resultados el servidor SHALL probar sub-frases contiguas cada vez más cortas y SHALL indicar en la respuesta (`nota`) que los resultados provienen de sub-frases.

#### Scenario: Frase sin coincidencia exacta
- **WHEN** se busca "contrato de trabajo mipymes" y no hay coincidencia literal
- **THEN** se devuelven las normas que coinciden con "contrato de trabajo" y se incluye una nota explicativa

### Requirement: Comportamiento conocido del filtro de estado
La herramienta SHALL documentar que el filtro `estado=Vigente` no devuelve resultados en el buscador del sitio.

#### Scenario: Filtro por estado
- **WHEN** se filtra por `Derogada` o `Modificada`
- **THEN** se devuelven resultados normalmente (10 por página, `page` base cero)

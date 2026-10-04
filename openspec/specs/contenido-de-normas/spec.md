# contenido-de-normas Specification

## Purpose
Obtener los metadatos y el texto íntegro de una norma a partir del PDF de la gaceta que la publica.

## Requirements

### Requirement: Metadatos de una norma
El servidor SHALL exponer `get_norma` que, dada la URL o el slug de una norma, devuelve título, identificador (p. ej. `GOC-2026-594-EX92`), número, año, resumen, palabras clave, normas que deroga, normas que la modifican, norma que la deroga y la gaceta que la publica (nombre completo, URL y PDF).

#### Scenario: Norma existente
- **WHEN** se pide `acuerdo-651-x-de-2026-de-consejo-de-estado`
- **THEN** se devuelve el identificador `GOC-2026-594-EX92` y la gaceta "Gaceta Oficial No. 92 Extraordinaria de 2026"

#### Scenario: Norma inexistente
- **WHEN** el slug no corresponde a ninguna norma
- **THEN** se devuelve un error claro sin lanzar excepción no controlada

### Requirement: Texto íntegro de la norma
`get_norma` SHALL devolver el texto íntegro de la norma extraído del PDF de su gaceta, desde su identificador hasta el identificador de la norma siguiente, sin los encabezados repetidos de página y con las palabras partidas por guion de fin de línea reunidas.

#### Scenario: Acuerdo completo
- **WHEN** se pide el Acuerdo 651-X de 2026
- **THEN** `texto` incluye "ACUERDO 651-X", sus apartados PRIMERO y SEGUNDO y la fórmula COMUNÍQUESE

#### Scenario: Texto largo
- **WHEN** el texto supera `max_chars`
- **THEN** se devuelve recortado con `truncado: true` y el total de caracteres, y se puede pedir más con `desde`

#### Scenario: Sin texto disponible
- **WHEN** la gaceta solo tiene un adjunto que no es PDF (p. ej. `.rar`) o el PDF no tiene texto extraíble
- **THEN** se devuelven los metadatos, el enlace de descarga y un `mensaje` que explica que el texto no está disponible

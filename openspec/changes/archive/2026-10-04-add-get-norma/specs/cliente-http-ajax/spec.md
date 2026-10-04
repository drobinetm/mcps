## ADDED Requirements

### Requirement: Descarga de PDFs
El cliente SHALL descargar documentos PDF de la gaceta con reintentos, timeout ampliado y un tamaño máximo (50 MB), y SHALL cachear en memoria los PDFs recientes para no repetir la descarga.

#### Scenario: PDF muy grande
- **WHEN** el PDF supera el tamaño máximo
- **THEN** se informa del enlace de descarga en lugar de procesarlo

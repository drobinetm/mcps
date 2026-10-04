# catalogos Specification

## Purpose
TBD - created by archiving change add-gaceta-mcp-server. Update Purpose after archive.

## Requirements

### Requirement: Catálogos de valores
El servidor SHALL exponer `list_catalogs` con tipos de edición, tipos de norma, estados y organismos con sus IDs reales del sitio, para que el agente mapee lenguaje natural a IDs válidos.

#### Scenario: Tipo de edición
- **WHEN** el usuario pide "extraordinarias"
- **THEN** se mapea al ID `3`

#### Scenario: Organismos
- **WHEN** se solicitan organismos
- **THEN** se cargan desde la página de búsqueda avanzada y se cachean en memoria

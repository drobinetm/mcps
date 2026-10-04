## ADDED Requirements

### Requirement: Búsqueda de gacetas por número, año y tipo
El servidor SHALL exponer `search_gacetas` que consulta `POST /es/getdatagaceta` con `numero`, `anno`, `t_edicion`, `page` y `buscar=1`.

#### Scenario: Gaceta concreta
- **WHEN** el usuario pide la Gaceta Extraordinaria No. 92 de 2026
- **THEN** se devuelve la gaceta con su fecha, tipo, número y enlace de descarga PDF

### Requirement: Índice de una gaceta
El servidor SHALL exponer `get_gaceta_indice` que consulta `POST /es/getdatagacetasa`.

#### Scenario: Sumario
- **WHEN** se solicita el índice de una gaceta existente
- **THEN** se devuelven las normas que contiene

## ADDED Requirements

### Requirement: Nombre completo de la gaceta
Toda gaceta devuelta por `list_ediciones`, `search_gacetas` y `search_gacetas_historicas` SHALL incluir `nombre_completo` con el formato "Gaceta Oficial No. {número} {tipo} de {año}".

#### Scenario: Gaceta extraordinaria
- **WHEN** se devuelve la edición Extraordinaria número 92 del 2 de octubre de 2026
- **THEN** `nombre_completo` es "Gaceta Oficial No. 92 Extraordinaria de 2026"

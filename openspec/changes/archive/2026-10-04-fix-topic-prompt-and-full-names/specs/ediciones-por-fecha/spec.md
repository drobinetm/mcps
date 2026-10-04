## MODIFIED Requirements

### Requirement: Contenido de cada edición
Cada edición devuelta SHALL incluir tipo, número, fecha, `nombre_completo` (p. ej. "Gaceta Oficial No. 92 Extraordinaria de 2026"), URL de la gaceta, URL del PDF y la lista de normas que contiene con su título completo y URL absoluta.

#### Scenario: Edición con normas
- **WHEN** una edición contiene normas
- **THEN** cada norma aparece con su título completo (p. ej. "Acuerdo 651-X de 2026 de Consejo de Estado") y URL absoluta

## ADDED Requirements

### Requirement: Marcado de normas por tema
`list_ediciones` SHALL aceptar `topics_` y, cuando se indiquen, marcar cada norma de las ediciones que coincida con algún tema (buscando en la búsqueda avanzada, filtrada por el año del periodo), incluyendo el tema coincidente y el resumen de la norma, y SHALL listar aparte las normas relevantes.

#### Scenario: Norma relevante
- **WHEN** una edición del periodo contiene una norma que la búsqueda avanzada devuelve para el tema "trabajo"
- **THEN** esa norma lleva `temas: ["trabajo"]` y su `resumen`, y aparece en `normas_relevantes`

#### Scenario: Ninguna coincidencia
- **WHEN** ninguna norma del periodo coincide con los temas
- **THEN** `normas_relevantes` está vacío y se indica en `mensaje_temas`

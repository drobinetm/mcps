# busqueda-gacetas Specification

## Purpose
Buscar gacetas por número, año y tipo, y consultar el archivo histórico con su índice; informar cuando no hay gacetas.

## Requirements

### Requirement: Búsqueda de gacetas por número, año y tipo
El servidor SHALL exponer `search_gacetas` que consulta `POST /es/getdatagaceta` con `numero`, `anno`, `t_edicion`, `page` y `buscar=1`.

#### Scenario: Gaceta concreta
- **WHEN** el usuario pide la Gaceta Extraordinaria No. 92 de 2026
- **THEN** se devuelve la gaceta con su fecha, tipo, número y enlace de descarga PDF

### Requirement: Archivo histórico de gacetas con índice
El servidor SHALL exponer `search_gacetas_historicas` que consulta `POST /es/getdatagacetasa` (página `/es/gacetas-oficiales-1990-2008`) con `numero`, `anno`, `t_edicion`, `indice` (texto a buscar en el índice), `page` y `buscar=1`, y SHALL devolver por cada gaceta su número, tipo, fecha, URL, enlace de descarga e índice (organismos y normas que contiene).

#### Scenario: Búsqueda en el índice
- **WHEN** se busca "trabajo" en las gacetas de 2001
- **THEN** se devuelven gacetas de 2001 cuyo índice contiene ese texto, con el índice estructurado por organismo

#### Scenario: Año fuera del archivo
- **WHEN** se busca en un año sin gacetas en el archivo histórico (por ejemplo 2026)
- **THEN** la respuesta tiene lista vacía y un `mensaje` que indica que no hay gacetas publicadas y que el archivo histórico solo cubre años anteriores a 2009

### Requirement: Respuesta explícita cuando no hay gacetas
Todas las herramientas que listan o buscan gacetas (`list_ediciones`, `search_gacetas`, `search_gacetas_historicas`) SHALL devolver un campo `mensaje` que indique que no hay gacetas publicadas cuando el resultado esté vacío, en lugar de una lista vacía sin explicación.

#### Scenario: Sin gacetas
- **WHEN** no existen gacetas para el periodo o los criterios pedidos
- **THEN** la respuesta incluye `mensaje: "No hay gacetas publicadas ..."` y `total` igual a 0

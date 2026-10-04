## ADDED Requirements

### Requirement: Reproducción de llamadas AJAX del sitio
El cliente SHALL realizar peticiones `POST` con `Content-Type: application/x-www-form-urlencoded` a `https://www.gacetaoficial.gob.cu/es/<endpoint>`, serializando los parámetros como `data[campo]=valor` y los arrays como `data[campo][]=valor`, con las cabeceras `X-Requested-With: XMLHttpRequest` y `Referer` de la página de origen.

#### Scenario: Sesión inicializada
- **WHEN** se realiza la primera petición AJAX
- **THEN** el cliente hace antes un `GET` a la página de origen para obtener cookies de sesión

#### Scenario: Fallo de red
- **WHEN** el sitio no responde dentro del timeout o devuelve un error 5xx
- **THEN** el cliente reintenta con espera creciente y, si persiste, devuelve un error claro a la herramienta

### Requirement: Parsing de fragmentos HTML
El cliente SHALL convertir los fragmentos HTML en estructuras tipadas, con URLs absolutas y datos de paginación (`page`, `has_more`).

#### Scenario: Respuesta vacía
- **WHEN** el endpoint devuelve cuerpo vacío o "No se encontraron resultados"
- **THEN** el resultado es una lista vacía sin error

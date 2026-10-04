## Why

Los usuarios quieren leer una norma completa (p. ej. un Acuerdo o una Resolución) desde el agente. La página de cada norma en el sitio solo trae metadatos y un resumen; el texto íntegro solo existe dentro del PDF de la gaceta que la publica.

## What Changes

- Nueva herramienta `get_norma(norma, max_chars)` que, a partir de la URL o el slug de una norma, devuelve sus metadatos (identificador GOC, número, año, gaceta, palabras clave, normas que deroga/modifica, resumen) y su **texto íntegro**.
- El texto se obtiene descargando el PDF de la gaceta, extrayendo su texto (pypdf) y recortando la sección que empieza en el identificador de la norma (`GOC-AAAA-N-XXX`) y termina en el siguiente identificador.
- Cacheo en memoria de los PDFs ya descargados; límite de caracteres con indicador de truncado.
- Nueva dependencia: `pypdf`.

## Capabilities

### New Capabilities
- `contenido-de-normas`: obtención de metadatos y texto íntegro de una norma.

### Modified Capabilities
- `cliente-http-ajax`: el cliente descarga también binarios (PDF) con límite de tamaño.

## Impact

La primera consulta de una gaceta grande puede tardar unos 15 s (descarga de varios MB y extracción de cientos de páginas). Las gacetas antiguas con adjunto `.rar` o PDF escaneado no tienen texto extraíble: se devuelve el enlace de descarga y un mensaje.

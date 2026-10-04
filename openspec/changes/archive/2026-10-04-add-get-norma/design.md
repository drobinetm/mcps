## Context

`/es/<slug-de-norma>` solo trae metadatos y resumen. El texto está en el PDF de la gaceta (`/sites/default/files/goc-AAAA-<tipo><n>.pdf`), que tiene texto extraíble y en el que cada norma empieza con una línea que contiene solo su identificador `GOC-AAAA-N-XXX`; el sumario lo lista entre paréntesis, por lo que no se confunde.

## Decisions

- **Flujo**: página de la norma -> identificador y enlace a la gaceta -> página de la gaceta -> URL del PDF -> descarga -> pypdf -> recorte por identificador.
- **pypdf** (puro Python, sin binarios) para que `uvx` funcione en Linux y Windows sin dependencias del sistema.
- **Limpieza**: se eliminan las líneas de pie/encabezado repetidas ("Gaceta Oficial de la República", fecha + `GOC-AAAA-Onn`, números de página sueltos) y se reúnen palabras partidas por guion de fin de línea.
- **Caché LRU en memoria** de los últimos PDFs (hasta 4) y límite de 50 MB.
- Gacetas antiguas con `.rar` o escaneadas: no se intenta OCR; se devuelve el enlace.

## Risks

- El formato de los PDFs puede variar entre épocas: si no se encuentra el identificador se devuelve mensaje y enlace, no un texto equivocado.
- Una gaceta grande tarda unos 15 s la primera vez.

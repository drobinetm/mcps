## 1. Cliente
- [x] 1.1 `get_bytes` con reintentos, límite de tamaño y caché LRU

## 2. Parsers
- [x] 2.1 `parse_norma_page` y `parse_gaceta_pdf_url` con fixtures reales
- [x] 2.2 `extract_norma_text` (recorte por identificador, limpieza, dehyphenation)
- [x] 2.3 Tests

## 3. Herramienta
- [x] 3.1 `get_norma(norma, max_chars, desde)` y mensajes de no disponibilidad
- [x] 3.2 Instrucciones del servidor: usar `get_norma` cuando el usuario pida leer una norma completa
- [x] 3.3 README y CHANGELOG
- [x] 3.4 Probar en vivo (Acuerdo 651-X y Resolución 28 de 2026)

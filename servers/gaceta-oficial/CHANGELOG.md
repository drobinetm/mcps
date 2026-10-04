# Changelog

## 0.1.0
- Primera versión: list_ediciones, search_normas, search_gacetas, search_gacetas_historicas, list_catalogs, get_topics, set_topics.

### Fixed
- `search_gacetas_historicas` (formerly `get_gaceta_indice`) always returned empty: its endpoint serves the 1990-2008 archive and uses a different result class. Gaceta tools now return an explicit message when there are no results.

## Unreleased
- New `get_norma` tool: metadata and full text of a norm, extracted from the PDF of its gaceta (adds the `pypdf` dependency).
- The agent now asks for a topic before any search, including date searches.
- `list_ediciones` accepts `topics_` and marks matching norms (`temas`, `resumen`, `normas_relevantes`).
- Gacetas include `nombre_completo`; instructions require full gaceta names and full norm titles with links.

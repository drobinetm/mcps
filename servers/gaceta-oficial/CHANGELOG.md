# Changelog

## 0.1.0
- Primera versión: list_ediciones, search_normas, search_gacetas, search_gacetas_historicas, list_catalogs, get_topics, set_topics.

### Fixed
- `search_gacetas_historicas` (formerly `get_gaceta_indice`) always returned empty: its endpoint serves the 1990-2008 archive and uses a different result class. Gaceta tools now return an explicit message when there are no results.

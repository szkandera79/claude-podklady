# podklady/ — MIMO GIT

Vše v této složce (kromě tohoto souboru) je v `.gitignore`: synchronizuje se jen přes iCloud,
na GitHub se nedostane.

- `snimky/` — snímky obrazovky IOT. Ukládej sem i anonymizované; do `tests/vzorky/`
  je přesune Claude až po kontrole anonymizace (docs/BEZPECNOST.md §5).
- `dokumentace/<model nebo řídicí jednotka>/` — PDF manuály Power World, seznamy chyb,
  schémata, dokumentace regulátorů, vlastní servisní poznatky.
- `katalog.yaml` — seznam dokumentů (název, model, řídicí jednotka, verze, jazyk, typ,
  oprávnění k užití). Založí Claude při importu (etapa 3).

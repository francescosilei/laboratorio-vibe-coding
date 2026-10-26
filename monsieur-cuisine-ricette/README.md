# Ricette per Monsieur Cuisine Connect

Web app personale per consultare, da un tablet in cucina, ricette pensate per il Bimby tradotte in
istruzioni passo passo per il Monsieur Cuisine Connect.

- elenco ricette con filtri per tipologia e paese, ricerca per titolo e per ingredienti
- scheda ricetta (foto, tempo, porzioni, difficoltà, ingredienti, procedimento) e modalità "Avvia"
  passo passo con pesata, manopole di tempo/velocità/temperatura, timer e schermata finale
- preferiti
- "cosa ho in casa": ricette che usano gli ingredienti inseriti, ordinate per ingredienti in comune

## Struttura

| Percorso | Contenuto |
|---|---|
| `data/ricette.json` | ricette e passi (generato da `tools/genera_ricette.py`) |
| `data/img/` | foto delle ricette |
| `app/template.html` | l'app (HTML, CSS, JS in un file) |
| `build.py` | compone `dist/index.html` con dati e foto incorporati |
| `docs/` | tabelle di conversione Bimby → Connect e formato dei passi |

Per rigenerare: `python3 tools/genera_ricette.py && python3 build.py`, poi si pubblica `dist/index.html`.

## Regole dei dati

Dato mancante = `NA`. Categoria e paese dedotti con alta confidenza sono elencati in `dedotto` e
marcati nella scheda. Le correzioni dette in chat prevalgono sulla deduzione. Ogni passo con una
conversione incerta ha un campo `avvertenza` mostrato in giallo.

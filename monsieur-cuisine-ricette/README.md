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
| `data/ricette/` | una ricetta per file (JSON) |
| `data/img/` | foto delle ricette |
| `app/template.html` | l'app (HTML, CSS, JS in un file) |
| `build.py` | compone `dist/index.html` con dati e foto incorporati |
| `tools/valida.py`, `tools/importa.py` | controllo di coerenza e meccanica dell'importazione |
| `import/` | `inbox/` screenshot da importare, `ok/` importati, `failed/` non importati |
| `docs/` | tabelle di conversione Bimby → Connect e formato dei passi |

Per rigenerare: `python3 build.py`, poi si pubblica `dist/index.html`.

## Importare nuove ricette

Screenshot in `import/inbox/` (o allegati in chat) e `/importa-ricette`: vedi `.claude/skills/importa-ricette/SKILL.md`
e `docs/formato-ricetta.md`. Controllo manuale: `python3 tools/valida.py`.

## Regole dei dati

Dato mancante = `NA`. Categoria e paese dedotti con alta confidenza sono elencati in `dedotto` e
marcati nella scheda. Le correzioni dette in chat prevalgono sulla deduzione. Ogni passo con una
conversione incerta ha un campo `avvertenza` mostrato in giallo.

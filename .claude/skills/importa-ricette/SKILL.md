---
name: importa-ricette
description: Importa nel Ricettario Connect le ricette Bimby fornite come PDF unico (una ricetta per pagina, screenshot di Cookidoo) o come screenshot, le traduce per il Monsieur Cuisine Connect, controlla la coerenza dei numeri, ripubblica l'app. Usa la lettura automatica del testo, senza aprire immagini in chat.
---

# Importa ricette

Lavora in `monsieur-cuisine-ricette/`. Regole: `docs/conversione-bimby-connect.md`, `docs/formato-passi.md`,
`docs/formato-ricetta.md`. Leggile prima della prima importazione della sessione.
Dipendenze: `pip install -r requirements.txt` (e `poppler-utils` per `pdfimages`).

## Metodo preferito: un PDF con tutte le ricette

L'utente unisce i PDF degli screenshot in un solo file e lo allega in chat (il file arriva in `/root/.claude/uploads/`).
Box non serve: da Box si vedono solo anteprime a metà risoluzione e ogni immagine entra in chat.

1. `python3 tools/pdf_ricette.py estrai FILE.pdf [FILE2.pdf ...] --out <scratchpad>/lotto`
   Una ricetta = un file PDF (le pagine sono fette dello screenshot e vengono riunite) o un segnalibro di un PDF combinato.
   Per ogni ricetta, in `lotto/<codice>/`: `testo.txt` (testa, ingredienti, preparazione già divisi), `foto.jpg`, `pagina.png`;
   in `lotto/indice.txt` il codice Cookidoo (`origine=cookidoo:rNNNNNN`) e le righe incerte.
   Il testo selezionabile aggiunto da Acrobat viene ignorato: è di qualità scarsa. Si legge l'immagine a piena risoluzione.
2. **Leggi solo i `testo.txt`** (testo, pochi token). Non aprire le pagine intere.
3. Le icone non sono nel testo ma lasciano un segno: `//` prima di `vel.` = rotazione antioraria (`sinistrorsa`);
   `vel. .` o `vel. s` = velocità cucchiaio (vel 1 + sinistrorsa). Un solo `/` = nessuna icona.
   Gli errori tipici dell'OCR sulle cifre sono corretti in automatico (1oo → 100).
4. **Frazioni:** l'OCR legge «¾» come `/4` e perde il numeratore. Ogni riga con `/2`, `/4` o `1/4` va verificata
   con un solo ritaglio piccolo (mai la pagina intera): `pagina.png.crop(box)` ingrandito 2x, tutte le righe in un'unica immagine.
   Le righe con `[?0.xx]` hanno bassa confidenza: stesso controllo.
5. Per ogni ricetta scrivi il JSON (formato in `docs/formato-ricetta.md`) nello scratchpad e aggiungi
   `"origine": "cookidoo:rNNNNNN"` (serve per evitare i duplicati).
6. `python3 tools/importa.py aggiungi ricetta.json --foto lotto/<codice>/foto.jpg` (la foto è già ritagliata).
   Il controllo `tools/valida.py` decide: nessun errore → importata. Errori → correggi o `fallita`.
7. `python3 tools/importa.py fallita <nome> "<motivo>"` per le non importate (scrive `import/failed/<nome>/motivo.txt`).
8. Pubblica `dist/index.html` su https://claude.ai/artifact/ThaxPn3qs2aLW18L1Cbq6J (stesso `file_path`, stesse capabilities),
   poi commit e push sul branch di lavoro.
9. Riepilogo breve all'utente: ricette importate, fallite e perché, campi `NA` o dedotti, passi con avvertenza.

## Metodo alternativo: screenshot singoli

Allegati in chat (max 5 per volta) o in `import/inbox/`: `python3 tools/importa.py stato`, poi lettura visiva con ritagli
ingranditi e `importa.py aggiungi ... --screenshot ... --foto ... --crop ...`. È molto più costoso in token: usarlo solo se manca il PDF.

## Cosa è ok e cosa è failed

- **ok:** il controllo non dà errori. Dati incerti (NA, dedotti, avvertenze, avvisi) restano e vanno nel riepilogo.
  Mai inventare un valore: se non è leggibile o non è nelle tabelle, `NA` o avvertenza.
- **failed:** errori del controllo non risolvibili, testo o numeri illeggibili, ricetta incompleta, duplicato.
  Il motivo va scritto in chiaro con cosa serve per riprovare.
- Categoria: le zuppe e le vellutate si classificano «Primi» (dedotto). Il «Paese» di Cookidoo è quello del catalogo e
  a volte è sbagliato (es. «Arabia Saudita»): se è implausibile, `NA` con una nota.
- Titoli, id o `origine` già presenti: non sovrascrivere mai; chiedi all'utente.

## Attenzione

- I grammi di ogni passo «pesata» devono coincidere con gli ingredienti; il testo di una pesata nomina solo l'ingrediente pesato.
- Le correzioni dell'utente in chat si applicano modificando `data/ricette/<id>.json`, poi
  `python3 tools/valida.py <id>`, `python3 build.py` e ripubblicare.

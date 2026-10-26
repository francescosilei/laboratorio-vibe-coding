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
2. **Bozza automatica per ogni ricetta:** `python3 tools/bozza.py lotto/<codice>/testo.txt --out <scratchpad>/<codice>.json`
   Scrive il JSON (formato `docs/formato-ricetta.md`, con `origine`) e stampa una vista compatta: una riga per passo
   (`P` pesata, `T` testo, `R` robot con tempo/velocità/temperatura/⟲, `⚠` se ha un'avvertenza), poi `ERRORE`, `avviso` e
   `DUBBIO` (frazioni `/4`, velocità non letta, ingrediente non trovato, paese anomalo, categoria non deducibile).
   **Non rileggere il JSON e non riscriverlo a mano:** controlla la vista e correggi solo ciò che è segnalato.
   Sulle 9 ricette scritte a mano il convertitore dà gli stessi passi del robot nel 100% dei casi (35/35), le stesse pesate
   nel 97% (61/63) e passa il controllo di coerenza in 9 casi su 9.
3. **Cosa controllare nella bozza** (poche righe a ricetta):
   - `ERRORE` e `DUBBIO`: correggi il JSON con un piccolo script Python o con `Edit`.
   - Frazioni: l'OCR legge «¾» come `/4` e perde il numeratore; le righe segnalate vanno verificate con UN ritaglio piccolo
     di `pagina.png` (mai la pagina intera). Le righe `[?0.xx]` nel `testo.txt` hanno bassa confidenza.
   - Icone: `//` prima di `vel.` = antiorario (`sinistrorsa`), `vel. .` / `vel. s` = velocità cucchiaio: la bozza le gestisce.
   - Categoria (zuppe e vellutate = «Primi», dedotto) e «Paese» di Cookidoo (a volte sbagliato, es. «Arabia Saudita» → `NA` con nota).
   - Varoma, Spiga, Cottura lenta, Sottovuoto, Bollitore, Copri Lame: la bozza li segna con un'avvertenza da tenere.
4. Importa: `python3 tools/importa.py aggiungi <scratchpad>/<codice>.json --foto lotto/<codice>/foto.jpg`
   (il controllo `tools/valida.py` decide; un `origine` già presente viene rifiutato come duplicato).
5. Se la bozza non è recuperabile (testo illeggibile, ricetta incompleta): `python3 tools/importa.py fallita <codice> "<motivo>"`.
6. Pubblica `dist/index.html` su https://claude.ai/artifact/ThaxPn3qs2aLW18L1Cbq6J (stesso `file_path`, stesse capabilities),
   poi commit e push sul branch di lavoro.
7. Riepilogo breve all'utente: ricette importate, fallite e perché, campi `NA` o dedotti, passi con avvertenza.

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

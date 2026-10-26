---
name: importa-ricette
description: Importa nel Ricettario Connect le ricette Bimby presenti come screenshot in monsieur-cuisine-ricette/import/inbox/ (o allegati in chat), le traduce per il Monsieur Cuisine Connect, controlla la coerenza dei numeri, sposta gli screenshot in ok/ o failed/ e ripubblica l'app.
---

# Importa ricette

Lavora in `monsieur-cuisine-ricette/`. Regole di traduzione e formato: `docs/conversione-bimby-connect.md`,
`docs/formato-passi.md`, `docs/formato-ricetta.md`. Leggile prima della prima importazione della sessione.

## Procedura

1. **Raccogli gli screenshot.** Se l'utente li ha allegati in chat, copiali in `import/inbox/`.
   Poi `python3 tools/importa.py stato`: elenca i file e segnala quelli poco leggibili.
   Gli indirizzi web non si usano: da questo ambiente i siti sono bloccati. Ignora eventuali `.txt`.
2. **Raggruppa** gli screenshot per ricetta (di solito scheda + foto, a volte una pagina sola).
3. **Per ogni ricetta**, leggi gli screenshot (ritaglia e ingrandisci con PIL le parti piccole) e scrivi un
   file JSON temporaneo nel formato di `docs/formato-ricetta.md`, nella cartella scratchpad:
   trascrizione fedele di ingredienti e procedimento, poi i `passi` tradotti per il Connect.
4. **Importa:** `python3 tools/importa.py aggiungi ricetta.json --screenshot ... --foto FILE --crop x0,y0,x1,y1`.
   Il comando esegue `tools/valida.py`: se non ci sono errori aggiunge la ricetta, ritaglia la foto,
   sposta gli screenshot in `import/ok/<id>/` e ricostruisce `dist/index.html`.
5. **Se ci sono errori**, la ricetta non viene toccata. Prima controlla se l'errore è un tuo errore di
   trascrizione (rileggi lo screenshot) e correggi. Se il problema è nella fonte o il testo è illeggibile,
   `python3 tools/importa.py fallita <nome> "<motivo>" file...`.
6. **Pubblica:** Artifact publish di `monsieur-cuisine-ricette/dist/index.html` sull'indirizzo
   https://claude.ai/artifact/ThaxPn3qs2aLW18L1Cbq6J (stesso `file_path`, non cambiare le capabilities).
7. **Commit e push** sul branch di lavoro (dati, foto, screenshot spostati).
8. **Riepilogo all'utente**, in italiano: ricette importate (con link), ricette in `failed/` e perché,
   campi `NA` o dedotti, e i passi con avvertenza da valutare sul robot. Una riga per ricetta.

## Cosa è ok e cosa è failed

- **ok:** il controllo non dà errori. Dati incerti (NA, dedotti, avvertenze, avvisi) restano in `ok/`
  e vanno nel riepilogo. Mai inventare un valore: se non è leggibile o non è nelle tabelle, `NA` o avvertenza.
- **failed:** errori del controllo non risolvibili (numeri incoerenti, ingredienti mai usati, duplicato),
  testo o numeri illeggibili, ricetta incompleta (mancano passi o ingredienti). Il motivo va scritto in chiaro,
  con cosa serve per riprovare (es. «rimanda lo screenshot della sola scheda, ingrandito»).
- Titoli o id già presenti: non sovrascrivere mai; chiedi all'utente.

## Attenzione

- Il numero di grammi di ogni passo «pesata» deve coincidere con gli ingredienti: rileggi sempre le cifre.
- Il testo di una pesata nomina solo l'ingrediente pesato (il controllo associa i grammi per nome).
- Le correzioni dell'utente in chat (categoria, paese, un passo) si applicano modificando
  `data/ricette/<id>.json`, poi `python3 tools/valida.py <id>`, `python3 build.py` e ripubblicare.

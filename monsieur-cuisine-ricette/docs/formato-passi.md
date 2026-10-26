# Formato dei passi sul Monsieur Cuisine Connect

Dedotto da 5 foto del display (ricetta ufficiale "Canederli in salsa di panna e gallinacci").
Layout comune: in alto Ricette / Menu avvio / Impostazioni, sotto il titolo della ricetta, in basso
barra di avanzamento con frecce indietro/avanti.

| # | Tipo di passo | Esempio | Elementi |
|---|---|---|---|
| 1 | Pesata + testo | "Tagliate 6 panini raffermi (400 g) a dadini di 1,5 x 1,5 cm." | bilancia a 0 g con tasto Tara, testo |
| 2 | Solo testo | "Versate i panini in una ciotola capiente e copriteli con 240 ml di latte. Fate riposare per 10 minuti. Nel frattempo eseguite il passaggio seguente." | testo, attesa (10 min) in parallelo al passo dopo |
| 3 | Comando robot | tempo 00:08, velocità 6, temperatura 0 °C | tre manopole (tempo / velocità / temperatura), icona lame, play e stop |
| 4 | Turbo | "Tenete premuto il tasto turbo per 2 secondi." | timer 00:00 con durata 00:02, icona turbo |
| 5 | Programma | ROSOLARE: 04:00, velocità 1 con icona di rotazione, 100 °C | tre manopole, nome programma, play e stop |

Da chiarire con Francesco: significato delle icone sotto la velocità (lame / accessorio), del
controllo "– I" in basso e del pulsante "i" (note o ingredienti?).

## Modello dati di un passo (bozza)

- `testo`: istruzione leggibile
- `pesata_g`: grammi da pesare (se presente), con tara
- `robot`: `{ tempo_s, velocita, temperatura_c, rotazione: "destra" | "sinistra", programma, accessorio, turbo }`
- `attesa_s`: attesa in parallelo (es. riposo 10 minuti)
- `avvertenza`: nota quando la conversione Bimby → Connect è "da valutare"

## Regola dei dati mancanti

Ogni dato non ricavabile dalla ricetta vale `NA`. Categoria e paese si inferiscono solo con
confidenza molto alta (pasta → primo, cioccolato/crema/zucchero → dessert); negli altri casi `NA`.
I campi inferiti sono marcati come tali. Le correzioni di Francesco in chat ("metti i canederli
al pesto come primi") vengono salvate come override sulla ricetta e prevalgono sull'inferenza.

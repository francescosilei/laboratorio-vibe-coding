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
| 6 | Comando robot con rotazione | 40:00, velocità 1 con icona freccia circolare, 120 °C | come il tipo 3; l'icona di rotazione compare anche nel passo ROSOLARE |
| 7 | Solo testo finale | "Servite la salsa di gallinacci con i canederli." | testo |
| 8 | Chiusura | foto del piatto con titolo, "BUON APPETITO!" e cuoricino (preferito) | foto a tutto schermo, solo freccia indietro |

## Chiarimenti di Francesco sul display

- La manopola centrale è la velocità di rotazione dell'accessorio. L'accessorio attivo è evidenziato:
  nel passo 3 sono le **lame** (sminuzzare).
- Sotto le lame compare in grigio e barrato con una X l'**emulsionatore** (accessorio di plastica per
  montare gli albumi o mescolare una minestra): non si può usare oltre una certa velocità perché
  rischia di rompersi. Quindi ogni passo robot indica l'accessorio da usare e quello vietato.
- Il controllo "– I" in basso cambia la modalità di navigazione dei passi: orizzontale (frecce
  < >, come nelle foto) o verticale (swipe dal basso verso l'alto per andare avanti, dall'alto verso
  il basso per tornare indietro).

## Decisione per l'app

Una sola modalità: pulsanti grandi Indietro / Avanti in basso. Più semplice e robusta dello swipe,
che sul tablet in cucina (mani sporche, schermo toccato per sbaglio) rischia di cambiare passo per
errore. Il tasto "i" non viene replicato.

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

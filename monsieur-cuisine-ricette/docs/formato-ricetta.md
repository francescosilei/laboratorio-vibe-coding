# Formato di una ricetta (`data/ricette/<id>.json`)

```json
{
  "id": "fregola-frutti-di-mare",          // minuscole, numeri, trattini; unico
  "titolo": "Fregola ai frutti di mare",
  "categoria": "Primi",                    // Antipasti|Primi|Secondi|Contorni|Dessert|Conserve|Creme|NA
  "paese": "Italia",                       // o "NA"
  "dedotto": ["categoria"],                // campi non scritti nella fonte ma dedotti con alta confidenza
  "tempo_prep_min": 10, "tempo_cottura_min": null, "tempo_min": 40,   // totale; null se non ricavabile
  "porzioni": 4, "difficolta": "Facile",   // "NA" se non indicata
  "fonte": "Bimby (Vorwerk)", "immagine": "fregola-frutti-di-mare.jpg",
  "ingredienti": [ { "testo": "250 g di fregola", "nome": "fregola", "gruppo": "facoltativo" } ],
  "procedimento": ["testo originale dei passi Bimby, senza numerazione"],
  "note": ["consigli della fonte"],
  "passi": [ ... ],                        // tradotti per il Connect, vedi sotto
  "importata": "2026-10-26"                // aggiunta in automatico
}
```

## Passi

| tipo | campi | uso |
|---|---|---|
| `pesata` | `g`, `testo`, `nota?` | ingrediente da pesare sulla bilancia |
| `testo` | `testo`, `attesa_s?`, `nota?`, `avvertenza?` | azione manuale, aggiunta senza pesata, riposo |
| `robot` | `testo`, `tempo_s`, `velocita`, `temp_c`, `sinistrorsa`, `programma?`, `nota?`, `avvertenza?` | impostazione del robot |

`nota` è un'informazione utile (box azzurro). `avvertenza` segnala una conversione da valutare (box giallo).

## Come si traduce un passo Bimby

- Ogni ingrediente in grammi aggiunto al boccale diventa una `pesata`; cucchiai, pizzichi, foglie e simili
  un `testo`. Poi viene il comando: un passo `robot`. Operazioni manuali («riunire sul fondo con la spatola») un `testo`.
- Il testo di una pesata nomina solo l'ingrediente pesato.
- `Soft` e `Antiorario`: velocità 1 con `sinistrorsa: true`. `Soffriggi` con 100° vel. 1: programma `Rosolare`.
  `Spiga`: programma `Impastare` (con avvertenza: durata gestita dal programma).
- Il Connect non ha mezze velocità (minimo 1, solo interi): arrotondare sempre per eccesso (0.5 → 1, 4.5 → 5), con l'avvertenza standard per 0.5.
- «Qualche secondo»: 5 s con avvertenza. «Tempo indicato sulla confezione»: `tempo_s: null` con `nota`.
- Funzioni non presenti nelle tabelle di conversione (Cottura lenta, Sottovuoto, Bollitore, Copri Lame,
  recipiente del Varoma usato come colino): si traducono al meglio e si segnano con `avvertenza`. Mai indovinare in silenzio.
- Un riposo «nel frattempo» è un `testo` con `attesa_s` (il timer resta attivo cambiando passo).

## Controlli automatici (`tools/valida.py`)

Errori (bloccano l'importazione): campi mancanti o fuori formato, velocità fuori 1-10, temperatura oltre 130 °C,
pesata senza ingrediente, grammi pesati diversi da quelli degli ingredienti, ingrediente mai usato nei passi, duplicati.
Avvisi: grammi usati solo nel testo, tempo o velocità mancanti senza spiegazione, programma non del Connect,
tempi dei passi superiori al tempo totale, ricetta senza foto.

# Conversione Bimby → Monsieur Cuisine Connect

Tabelle di riferimento fornite da Francesco (screenshot del 2026-10-26). Sono la base per tradurre
le istruzioni delle ricette Bimby in istruzioni per il Monsieur Cuisine Connect.

Le equivalenze sono **indicative**: dove la tabella dice "da valutare" o "secondo ricetta", la
conversione non va indovinata ma segnalata nel passo della ricetta.

## 1. Tabella delle velocità

| Funzione o velocità Bimby | Equivalenza indicativa sul Connect | Uso tipico |
|---|---|---|
| Soft / velocità cucchiaio | Velocità 1 + rotazione sinistrorsa; accessorio mixer se opportuno | Mescolare delicatamente senza triturare |
| Velocità 1 | Velocità 1 | Mescolare lentamente |
| Velocità 2 | Velocità 2 | Mescolare e amalgamare |
| Velocità 3 | Velocità 3 | Miscelare e lavorare ingredienti morbidi |
| Velocità 4 | Velocità 4 | Frullare o montare, secondo accessorio e ricetta |
| Velocità 5 | Velocità 5 | Tritare mediamente fine |
| Velocità 6 | Velocità 6 | Tritare e sminuzzare più finemente |
| Velocità 7 | Velocità 7 | Tritare fine, grattugiare |
| Velocità 8 | Velocità 8 | Tritare molto fine, macinare |
| Velocità 9 | Velocità 9 | Macinare e polverizzare |
| Velocità 10 | Velocità 10 o Turbo per impulsi brevi | Polverizzare ingredienti duri, secondo ricetta |
| Turbo | Turbo, tenendo premuto il comando | Tritatura intensa e rapida |

## 2. Corrispondenza delle funzioni speciali

| Funzione Bimby | Impostazione sul Monsieur Cuisine Connect | Note pratiche |
|---|---|---|
| Soft / cucchiaio | Velocità 1 + rotazione sinistrorsa | Per mescolare delicatamente |
| Antiorario | Rotazione sinistrorsa + velocità da 1 a 3 | Aiuta a preservare gli ingredienti; non equivale a lame ferme |
| Spiga | Programma automatico *Impastare* | Per impasti; non sostituire automaticamente con una velocità manuale |
| Varoma | Programma *Cottura al vapore* | Usa la vaporiera; segui i tempi della ricetta e considera il preriscaldamento |
| Soffriggere | Programma *Rosolare* | Impostazioni gestite dal programma, con possibilità di regolare alcuni parametri |
| Farfalla | Accessorio mixer del Connect | Da usare per montare o lavorare preparazioni fluide compatibili |
| Frullare / omogeneizzare | Parti da velocità bassa e aumenta gradualmente | La velocità finale dipende dalla consistenza desiderata |
| Emulsionare | Accessorio mixer, generalmente velocità 1–4, se adatto alla ricetta | Per esempio maionese e salse |
| Tritare / macinare | Lame, velocità variabile da 5 a 10 o Turbo | Parti con impulsi brevi e controlla il risultato |
| Pesare | Bilancia integrata | Funzione equivalente, con tara |
| Temperatura Varoma in una preparazione nel boccale | Da valutare in base alla ricetta; il Connect raggiunge temperature fino a 130 °C | Non sostituire automaticamente Varoma con 120 °C: la modalità di cottura conta |

Le corrispondenze relative a *Impastare*, *Cottura al vapore*, *Rosolare*, rotazione sinistrorsa e
accessorio mixer sono coerenti con il manuale del Connect e con le guide di conversione.

## Note per l'implementazione

- Nei dati delle ricette ogni passo del robot usa campi strutturati (velocità, temperatura, tempo,
  rotazione, programma, accessorio), non testo libero, così l'app può evidenziarli.
- I casi "da valutare" (Varoma nel boccale, Spiga, Antiorario) vanno marcati con un'avvertenza
  visibile nel passo.

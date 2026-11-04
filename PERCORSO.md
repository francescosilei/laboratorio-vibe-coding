# Percorso di apprendimento del vibe coding

Questo file riassume il piano concordato. All'inizio di ogni nuova sessione basta scrivere:
**"Leggi PERCORSO.md e iniziamo il progetto N"**.

## Chi sono (contesto per Claude)

- Ingegnere delle telecomunicazioni con esperienza in aziende SaaS B2B: delivery, supporto, operations director di gruppi R&D. Non ho mai scritto codice.
- Al momento sono in cerca di lavoro. La ricerca di lavoro (tracker delle offerte, analisi del fit, supporto alle candidature) è **già gestita** con Claude Cowork: non va duplicata.
- Uso un telefono Android e un PC Windows. Conosco Excel, Google Sheets, Notion e Trello, e in passato ho fatto un sito WordPress.

## Regole del laboratorio

1. **Obiettivo didattico.** Tanti piccoli progetti, ognuno da 1–2 sessioni.
2. **Carino e funzionante.** Conta il risultato, non serve capire nel dettaglio cosa c'è "sotto il cofano". Le spiegazioni vanno date in italiano semplice, solo quando servono.
3. **Funziona su telefono e PC.** Ogni pagina deve essere comoda sia su Android sia su Windows.
4. **Condivisibile con un link.** Chi lo riceve lo apre dal browser, senza registrazioni né installazioni. Ogni progetto viene pubblicato come Artifact su claude.ai.
5. **Prima la scheda, poi il codice.** Si parte concordando cosa fa la prima versione e cosa si rimanda a dopo.
6. **Credito.** Il credito è limitato: va usata una sessione nuova per ogni progetto, con richieste chiare e raggruppate. A fine progetto si controlla quanto si è speso.
7. **Tutto nel repository.** Ogni progetto ha la sua cartella (`01-...`, `02-...`) e viene salvato su GitHub come copia di sicurezza.

## I 4 progetti

| # | Progetto | Cosa fa | Cosa imparo | Sessioni |
|---|----------|---------|-------------|----------|
| 1 | **Pagina professionale personale** | Una pagina curata con profilo, esperienze, cosa cerco e contatti, da linkare su LinkedIn o nelle email | Come si costruisce e si rende bella una pagina web, adatta a PC e telefono, e come si pubblica con un link | 1 |
| 2 | **Suite di benessere** (per l'attività di psicologa di mia moglie) | Un piccolo sito di strumenti per fermarsi e ritrovare calma: si parte da "Respira con me" (fatto, prima versione) e si aggiungono altri strumenti uno alla volta. Non raccoglie dati personali | Interattività (animazioni, pulsanti, timer, suoni), audio con la voce di mia moglie e lavoro per un "cliente" reale, con raccolta di requisiti e feedback | 1 per tappa |
| 3 | **"Chi porta cosa"** per famiglia e amici | Una lista condivisa via link: ognuno scrive nome e cosa porta, e tutti vedono gli aggiornamenti | Come un'app ricorda i dati e li condivide tra più persone, senza registrazioni | 1–2 |
| 4 | **Simulatore di colloquio con l'AI** | Scelgo il ruolo, l'app mi fa domande da recruiter e alla fine mi dà un riscontro | Come inserire l'intelligenza artificiale dentro un'app | 2 |

**Progressione:** pagina statica → interattività → dati condivisi → AI.

## Note da verificare

- **Progetto 4:** prima di costruirlo, chiarire chi paga le chiamate a Claude fatte dall'app quando qualcuno la usa.

## Progetto 2: tappe della suite

Cartella: `02-respirazione-guidata/`. Un solo sito, un link per strumento, nessun account e nessun dato inviato: le risposte restano sul dispositivo. Una sessione nuova per ogni tappa.

- [x] **Respira con me**: prima versione con 4 esercizi, timer, suono e vibrazione facoltativi, contatti in fondo
- [x] **Pagina iniziale "Un momento per te"**: tre domande (bisogno, tempo, come essere guidato) e pulsante "Prova il mio percorso"
- [x] **Torna al presente**: versione solo testo e timer (1 e 5 minuti), prima versione
- [x] **Cassetta degli attrezzi**: scegli una situazione e ricevi una piccola attività
- [x] **Fai spazio ai pensieri**: diario guidato, risposte salvate solo sul dispositivo
- [x] **Voce di mia moglie**: sezioni A-F registrate e inserite nell'app (respiro, torna al presente, sonno, riflessione sulla gentilezza). Istruzioni in `02-respirazione-guidata/registrazioni-voce.docx`; script di divisione in `02-respirazione-guidata/strumenti/`
- [x] **Come mi sento adesso**: scelta dell'emozione, intensità su scala, attività coerente e verifica finale (prima versione)
- [x] **Accompagna il sonno**, **Parla a te stesso con gentilezza**, **Prima di una conversazione difficile**: prime versioni con testi miei, da far rivedere a mia moglie (il sonno è solo testo, l'audio con la sua voce arriva dopo)

Da decidere con mia moglie: numeri di aiuto da mostrare, nome da usare nell'intestazione, testi clinici da far rivedere a lei prima della pubblicazione. Il dominio personale è rimandato.

## Pubblicazione online (decisione del 5 novembre)

Si pubblica lo stesso sito su **GitHub Pages** e su **Netlify**, per confrontarli; in futuro si tiene il migliore. Il sito è la cartella `sito/` (costruita da `02-respirazione-guidata/strumenti/costruisci_sito.py`): pagina leggera (circa 90 KB), audio in file separati caricati solo quando servono, icone dal logo a spirale, caratteri inclusi nel sito. Va messa da sola in un repository nuovo e pubblico (`un-momento-per-te`): niente registrazioni intere, appunti o questo file.

- [x] Pagina autonoma, audio separato, icone, manifest, prove su un server vero (radice e sottocartella)
- [ ] Repository pubblico del sito, con la sola cartella `sito/` alla radice
- [ ] Attivare GitHub Pages (Settings, Pages, Deploy from a branch, main, root)
- [ ] Collegare Netlify allo stesso repository; disattivare anteprime e pubblicazioni dei rami
- [ ] Testo della privacy, avviso sui diritti delle registrazioni, numeri di aiuto (da tua moglie)
- [ ] Togliere «noindex» e robots.txt quando si decide di rendere il sito visibile ai motori di ricerca
- [ ] Prova finale su telefono con Brave: installazione, icona, voce

## Materiale da preparare per il progetto 1

- Un breve profilo (2–3 righe)
- Le esperienze principali (aziende, ruoli, anni, 1–2 risultati per ciascuna)
- Il tipo di ruolo che cerco
- I contatti da mostrare (per esempio LinkedIn ed email)
- Una foto (facoltativa)

Va bene anche copiare i testi dal profilo LinkedIn.

## Stato

- [ ] Progetto 1: Pagina professionale
- [ ] Progetto 2: Suite di benessere (a tappe)
- [ ] Progetto 3: Chi porta cosa
- [ ] Progetto 4: Simulatore di colloquio

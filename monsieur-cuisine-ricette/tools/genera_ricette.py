"""Genera data/ricette.json dalle ricette Bimby trascritte e tradotte per il Monsieur Cuisine Connect.

Convenzioni (vedi docs/conversione-bimby-connect.md):
- dato non ricavabile -> "NA"; dato dedotto -> campo elencato in "dedotto"
- Soft = velocita 1 + rotazione sinistrorsa; Antiorario = sinistrorsa (vel 1)
- "avvertenza" = conversione da valutare; "nota" = informazione utile
"""
import json, pathlib

def P(g, testo, nota=None):
    return {"tipo": "pesata", "g": g, "testo": testo, **({"nota": nota} if nota else {})}

def T(testo, attesa_s=None, nota=None, avvertenza=None):
    d = {"tipo": "testo", "testo": testo}
    if attesa_s: d["attesa_s"] = attesa_s
    if nota: d["nota"] = nota
    if avvertenza: d["avvertenza"] = avvertenza
    return d

def R(testo, tempo_s, velocita, temp_c=0, sinistrorsa=False, programma=None, nota=None, avvertenza=None):
    d = {"tipo": "robot", "testo": testo, "tempo_s": tempo_s, "velocita": velocita,
         "temp_c": temp_c, "sinistrorsa": sinistrorsa}
    if programma: d["programma"] = programma
    if nota: d["nota"] = nota
    if avvertenza: d["avvertenza"] = avvertenza
    return d

def I(testo, nome, gruppo=None):
    d = {"testo": testo, "nome": nome}
    if gruppo: d["gruppo"] = gruppo
    return d

SOFT = "Soft/Antiorario: velocità 1 con rotazione sinistrorsa."
CONF = "Il tempo dipende dalla confezione: controllatelo e impostatelo voi."

ricette = []

# ---------------------------------------------------------------- Vitello al curry
ricette.append({
    "id": "vitello-al-curry", "titolo": "Vitello al curry",
    "categoria": "Secondi", "paese": "NA", "dedotto": [],
    "tempo_prep_min": 4, "tempo_cottura_min": 22, "tempo_min": 26,
    "porzioni": 4, "difficolta": "NA",
    "fonte": "Ricette Bimby (Flavia)", "immagine": "vitello-al-curry.jpg",
    "ingredienti": [
        I("350 g di patate novelle", "patate novelle"),
        I("100 g di cipolla rossa", "cipolla rossa"),
        I("40 g di olio extravergine d'oliva", "olio extravergine d'oliva"),
        I("Sale q.b.", "sale"), I("Pepe q.b.", "pepe"),
        I("50 g di vino bianco", "vino bianco"),
        I("Zenzero fresco q.b.", "zenzero"),
        I("200 g di latte di cocco", "latte di cocco"),
        I("2 cucchiaini abbondanti di curry in polvere", "curry"),
        I("500 g di bocconcini di vitello", "vitello"),
        I("3 foglie di alloro", "alloro"), I("4 foglie di salvia", "salvia"),
        I("Ginepro q.b.", "ginepro"),
    ],
    "procedimento": [
        "Pela 350 g di patate novelle e tienile da parte.",
        "Metti nel boccale 100 g di cipolla rossa e trita 5 Sec. Vel. 6. Porta sul fondo con la spatola.",
        "Aggiungi 40 g di olio extravergine d'oliva e soffriggi 3 Min. 100° Vel. 1.",
        "Aggiungi le patate novelle pelate, una presa di sale, un pizzico di pepe, 50 g di vino bianco, una grattata abbondante di zenzero fresco e cuoci 7 Min. 100° Antiorario Vel. Soft.",
        "Versa 200 g di latte di cocco, unisci 2 cucchiaini abbondanti di curry in polvere, 500 g di bocconcini di vitello, 3 foglie di alloro, 4 foglie di salvia, qualche bacca di ginepro e cuoci 15 Min. 100° Antiorario Vel. Soft.",
        "Servi il vitello al curry con un'insalatina, del riso in bianco o con un pane chapati.",
    ],
    "note": [
        "Al posto del latte di cocco, se non ti piace, usa del brodo vegetale. In questo caso infarina leggermente la carne prima di versarla nel boccale, così da far rapprendere di più il sugo finale.",
    ],
    "passi": [
        P(350, "Pesate 350 g di patate novelle, pelatele e tenetele da parte."),
        P(100, "Pesate nel boccale 100 g di cipolla rossa."),
        R("Tritate la cipolla.", 5, 6),
        T("Portate sul fondo con la spatola."),
        P(40, "Pesate nel boccale 40 g di olio extravergine d'oliva."),
        R("Soffriggete.", 180, 1, 100, sinistrorsa=True, programma="Rosolare",
          avvertenza="Nella ricetta Bimby è «soffriggi» a velocità 1: il programma Rosolare del Connect gestisce da solo velocità e rotazione. Controllate i valori sul display."),
        T("Aggiungete le patate novelle pelate, una presa di sale, un pizzico di pepe e una grattata abbondante di zenzero fresco."),
        P(50, "Pesate nel boccale 50 g di vino bianco."),
        R("Cuocete.", 420, 1, 100, sinistrorsa=True, nota=SOFT),
        P(200, "Pesate nel boccale 200 g di latte di cocco."),
        P(500, "Unite 500 g di bocconcini di vitello."),
        T("Unite 2 cucchiaini abbondanti di curry in polvere, 3 foglie di alloro, 4 foglie di salvia e qualche bacca di ginepro."),
        R("Cuocete.", 900, 1, 100, sinistrorsa=True, nota=SOFT),
        T("Servite il vitello al curry con un'insalatina, del riso in bianco o con un pane chapati."),
    ],
})

# ---------------------------------------------------------------- Farrotto alle zucchine
ricette.append({
    "id": "farrotto-zucchine", "titolo": "Farrotto alle zucchine cremoso",
    "categoria": "Primi", "paese": "Italia", "dedotto": [],
    "tempo_prep_min": 3, "tempo_cottura_min": 40, "tempo_min": 43,
    "porzioni": 4, "difficolta": "NA",
    "fonte": "Ricette Bimby (Flavia)", "immagine": "farrotto-zucchine.jpg",
    "ingredienti": [
        I("40 g di cipolla a metà", "cipolla"),
        I("30 g olio extravergine di oliva", "olio extravergine d'oliva"),
        I("200 g di zucchine", "zucchine"),
        I("560 g di acqua", "acqua"),
        I("1 cucchiaio di dado vegetale", "dado vegetale"),
        I("280 g di farro perlato", "farro"),
        I("80 g di stracchino", "stracchino"),
    ],
    "procedimento": [
        "Mettere nel boccale 40 g di cipolla e trita Qualche Sec. Vel. 7.",
        "Riunire sul fondo con la spatola ciò che è finito sui bordi del boccale.",
        "Aggiungi 30 g di olio extravergine di oliva e insaporisci 3 Min. 120° Vel. 1.",
        "Aggiungi 200 g di zucchine tagliandole a cubetti e cuoci 5 Min. 120° antiorario Vel.1.",
        "Aggiungi 560 g di acqua, un cucchiaio di dado vegetale e 280 g di farro, cuoci per il tempo indicato dalla confezione 100° antiorario Vel. cucchiaio.",
        "Aggiungi 80 g di stracchino e mescola con la spatola.",
        "Lascia riposare 5 Min. nel boccale prima di servire.",
    ],
    "note": [
        "Se utilizzi una qualità di farro diversa (es. farro integrale) ti basta adattare il tempo di cottura in base alle indicazioni riportate sulla confezione. Tieni a portata di mano dell'acqua calda da aggiungere in caso di necessità.",
    ],
    "passi": [
        P(40, "Pesate nel boccale 40 g di cipolla a metà."),
        R("Tritate la cipolla.", 5, 7,
          avvertenza="La ricetta dice «qualche secondo»: 5 secondi è indicativo. Controllate il trito."),
        T("Riunite sul fondo con la spatola ciò che è finito sui bordi del boccale."),
        P(30, "Pesate nel boccale 30 g di olio extravergine di oliva."),
        R("Insaporite.", 180, 1, 120),
        P(200, "Pesate 200 g di zucchine tagliate a cubetti e versatele nel boccale."),
        R("Cuocete.", 300, 1, 120, sinistrorsa=True),
        P(560, "Pesate nel boccale 560 g di acqua."),
        T("Aggiungete 1 cucchiaio di dado vegetale."),
        P(280, "Pesate nel boccale 280 g di farro perlato."),
        R("Cuocete per il tempo indicato sulla confezione del farro.", None, 1, 100, sinistrorsa=True,
          nota=CONF + " " + SOFT),
        P(80, "Aggiungete 80 g di stracchino."),
        T("Mescolate con la spatola."),
        T("Lasciate riposare 5 minuti nel boccale prima di servire.", attesa_s=300),
    ],
})

# ---------------------------------------------------------------- Risotto zucca e gorgonzola
ricette.append({
    "id": "risotto-zucca-gorgonzola", "titolo": "Risotto zucca e gorgonzola",
    "categoria": "Primi", "paese": "Italia", "dedotto": ["paese"],
    "tempo_prep_min": 5, "tempo_cottura_min": 30, "tempo_min": 35,
    "porzioni": 4, "difficolta": "Bassa",
    "fonte": "RicettePerBimby", "immagine": "risotto-zucca-gorgonzola.jpg",
    "ingredienti": [
        I("Mezza cipolla", "cipolla"),
        I("500 g (pulita) zucca", "zucca"),
        I("30 g olio extravergine di oliva", "olio extravergine d'oliva"),
        I("600 g acqua", "acqua"),
        I("1 dado vegetale", "dado vegetale"),
        I("300 g riso Carnaroli", "riso carnaroli"),
        I("Sale fino q.b.", "sale"),
        I("30 g burro", "burro"),
        I("Gorgonzola (dolce) q.b.", "gorgonzola"),
        I("Parmigiano (grattugiato) q.b.", "parmigiano"),
    ],
    "procedimento": [
        "Mettere nel boccale la cipolla a fettine e la zucca a tocchetti: 15 sec. vel. 5.",
        "Raccogliere sul fondo: 15 sec. vel. 5.",
        "Raccogliere sul fondo e aggiungere l'olio: 3 min. 100° vel. 1.",
        "Aggiungere l'acqua e il dado: 10 min. 100° vel. 1.",
        "Aggiungere il riso e il sale: tempo indicato sulla confezione 100° vel. 1 antiorario.",
        "Aggiungere il burro e il gorgonzola a tocchetti: 2 min. 100° vel. Soft antiorario.",
        "Impiattare, cospargere con del parmigiano, del gorgonzola a dadini e servire.",
    ],
    "note": [],
    "passi": [
        T("Tagliate mezza cipolla a fettine."),
        P(500, "Pesate nel boccale 500 g di zucca pulita, a tocchetti, e aggiungete la cipolla."),
        R("Tritate.", 15, 5),
        T("Raccogliete sul fondo con la spatola."),
        R("Tritate ancora.", 15, 5, nota="Come da ricetta originale."),
        T("Raccogliete sul fondo con la spatola."),
        P(30, "Pesate nel boccale 30 g di olio extravergine di oliva."),
        R("Soffriggete.", 180, 1, 100),
        P(600, "Pesate nel boccale 600 g di acqua."),
        T("Aggiungete 1 dado vegetale."),
        R("Cuocete.", 600, 1, 100),
        P(300, "Pesate nel boccale 300 g di riso Carnaroli."),
        T("Aggiungete sale fino q.b."),
        R("Cuocete per il tempo indicato sulla confezione del riso.", None, 1, 100, sinistrorsa=True, nota=CONF),
        P(30, "Pesate nel boccale 30 g di burro."),
        T("Aggiungete il gorgonzola dolce a tocchetti."),
        R("Mantecate.", 120, 1, 100, sinistrorsa=True, nota=SOFT),
        T("Impiattate, cospargete con parmigiano grattugiato e gorgonzola a dadini. Servite."),
    ],
})

# ---------------------------------------------------------------- Filetto di maiale con salsa ai cachi
ricette.append({
    "id": "filetto-maiale-cachi", "titolo": "Filetto di maiale con salsa ai cachi",
    "categoria": "Secondi", "paese": "Italia", "dedotto": ["categoria"],
    "tempo_prep_min": 30, "tempo_cottura_min": None, "tempo_min": 120,
    "porzioni": 6, "difficolta": "Media",
    "fonte": "Bimby (Vorwerk)", "immagine": "filetto-maiale-cachi.jpg",
    "ingredienti": [
        I("200 g di cachi, sbucciati e a pezzi", "cachi", "Salsa ai cachi"),
        I("1 cucchiaino di zucchero di canna", "zucchero di canna", "Salsa ai cachi"),
        I("20 g di burro", "burro", "Salsa ai cachi"),
        I("60 g di vino passito", "vino passito", "Salsa ai cachi"),
        I("1200 g di acqua", "acqua", "Filetto"),
        I("30 g di succo di limone", "limone", "Filetto"),
        I("1 filetto di maiale, senza nervi (intero, 600-700 g circa)", "filetto di maiale", "Filetto"),
        I("200 g di pancetta, a fette", "pancetta", "Filetto"),
        I("2-3 pizzichi di sale", "sale", "Filetto"),
        I("2-3 pizzichi di pepe nero macinato", "pepe", "Filetto"),
    ],
    "procedimento": [
        "Salsa ai cachi. Mettere nel boccale i cachi, lo zucchero di canna e il burro, insaporire: 5 min./100°C/vel. 1.",
        "Aggiungere il vino passito e cuocere: 5 min./100°C/vel. 1 senza misurino, poi posizionare il misurino e frullare: 10 sec./vel. 8. Trasferire in una ciotola e tenere da parte. Lavare il boccale.",
        "Filetto. Posizionare il Copri Lame. Mettere nel boccale l'acqua e il succo di limone, impostare Bollitore/80°C. Nel frattempo, preparare il filetto di maiale.",
        "Dividere il filetto in 2 parti. Stendere sul piano di lavoro 2 fogli di pellicola trasparente resistente al calore e sistemare sopra ciascuno 100 g di pancetta, sovrapponendo leggermente le fette fino a formare dei rettangoli. Sistemare al centro di ciascun rettangolo di pancetta il filetto di maiale e insaporire con sale e pepe. Arrotolare tutto il filetto con la pancetta poi avvolgerlo bene nella pellicola trasparente, chiudendo le estremità. Sistemare ciascun filetto in 1 sacchetto per sottovuoto e sigillare con l'apposita macchina.",
        "Sistemare nel boccale i sacchetti con i filetti, aiutandosi con una pinza da cucina e assicurandosi che siano completamente immersi nell'acqua, impostare Sottovuoto/1 h 30 min./75°C. Togliere i sacchetti dal boccale con l'aiuto della pinza.",
        "Scaldare una padella antiaderente su fuoco medio-alto. Togliere i filetti dai sacchetti, srotolarli dalla pellicola trasparente e poi scottarli facendoli dorare qualche minuto su tutti i lati.",
        "Sistemare il filetto su un tagliere e tagliarlo a fette (2-3 cm). Servire accompagnando con la salsa ai cachi.",
    ],
    "note": [
        "Per la cottura sottovuoto utilizzare sacchetti resistenti ai tempi e alle temperature previste: specifici per alimenti e per cottura sottovuoto, resistenti fino a 100 °C e a 8 ore di cottura, BPA free e PVC free.",
    ],
    "passi": [
        P(200, "Pesate nel boccale 200 g di cachi sbucciati e a pezzi."),
        P(20, "Aggiungete 20 g di burro."),
        T("Aggiungete 1 cucchiaino di zucchero di canna."),
        R("Insaporite.", 300, 1, 100),
        P(60, "Pesate nel boccale 60 g di vino passito."),
        R("Cuocete senza misurino.", 300, 1, 100,
          nota="Senza misurino: lasciate aperto il foro del coperchio, come nella ricetta."),
        T("Posizionate il misurino."),
        R("Frullate.", 10, 8),
        T("Trasferite la salsa in una ciotola e tenetela da parte. Lavate il boccale."),
        T("Posizionate il Copri Lame.",
          avvertenza="Il Copri Lame è un accessorio del Bimby: non è nelle tabelle di conversione. Verificate se serve sul Connect."),
        P(1200, "Pesate nel boccale 1200 g di acqua."),
        P(30, "Aggiungete 30 g di succo di limone."),
        R("Scaldate l'acqua a 80 °C.", None, None, 80,
          avvertenza="Modalità Bollitore del Bimby: non è nelle tabelle. Il Connect arriva a 130 °C, ma verificate sul display come impostare la sola temperatura senza tempo e senza velocità."),
        T("Nel frattempo preparate il filetto di maiale: dividetelo in 2 parti. Stendete sul piano di lavoro 2 fogli di pellicola trasparente resistente al calore e sistemate sopra ciascuno 100 g di pancetta, sovrapponendo leggermente le fette fino a formare dei rettangoli."),
        T("Sistemate al centro di ciascun rettangolo di pancetta il filetto di maiale e insaporite con sale e pepe. Arrotolate il filetto con la pancetta, avvolgetelo bene nella pellicola trasparente e chiudete le estremità."),
        T("Sistemate ciascun filetto in 1 sacchetto per sottovuoto e sigillate con l'apposita macchina.",
          nota="Usate sacchetti per cottura sottovuoto resistenti fino a 100 °C e a 8 ore, BPA free e PVC free."),
        T("Sistemate nel boccale i sacchetti con i filetti, aiutandovi con una pinza da cucina. Assicuratevi che siano completamente immersi nell'acqua."),
        R("Cottura sottovuoto.", 5400, None, 75,
          avvertenza="Modalità Sottovuoto del Bimby (1 h 30 min a 75 °C): non è nelle tabelle e la velocità non è indicata. Verificate come impostarla sul Connect."),
        T("Togliete i sacchetti dal boccale con l'aiuto della pinza."),
        T("Scaldate una padella antiaderente su fuoco medio-alto. Togliete i filetti dai sacchetti, srotolateli dalla pellicola e scottateli facendoli dorare qualche minuto su tutti i lati."),
        T("Sistemate il filetto su un tagliere e tagliatelo a fette (2-3 cm). Servite accompagnando con la salsa ai cachi."),
    ],
})

# ---------------------------------------------------------------- Tacos integrali con pulled pork alla birra
ricette.append({
    "id": "tacos-pulled-pork", "titolo": "Tacos integrali con pulled pork alla birra",
    "categoria": "Secondi", "paese": "Messico", "dedotto": ["categoria", "paese"],
    "tempo_prep_min": 30, "tempo_cottura_min": None, "tempo_min": 300,
    "porzioni": 6, "difficolta": "Media",
    "fonte": "Bimby (Vorwerk)", "immagine": None,
    "ingredienti": [
        I("400-450 g di farina integrale (circa il 16% di contenuto proteico) + q.b.", "farina integrale"),
        I("290 g di acqua bollente", "acqua"),
        I("30 g di olio extravergine di oliva", "olio extravergine d'oliva"),
        I("2 cucchiaini di sale", "sale"),
        I("4 spicchi di aglio", "aglio"),
        I("150 g di cipolle, a metà", "cipolla"),
        I("800 g di spalla di maiale, senza ossa, in 5 pezzi", "spalla di maiale"),
        I("500 g di birra, stout", "birra"),
        I("150 g di acqua", "acqua"),
        I("70-80 g di miele", "miele"),
        I("2 cucchiaini di paprika in polvere, affumicata", "paprika"),
        I("1 cucchiaino di cumino in polvere", "cumino"),
        I("2 cucchiai di miso", "miso"),
        I("1 bacca di anice stellato", "anice stellato"),
        I("1 stecca di cannella, a metà", "cannella"),
        I("2 cucchiai di zucchero grezzo", "zucchero"),
        I("80 g di cipolla rossa, tritata", "cipolla rossa"),
        I("Foglie di coriandolo, fresche, a piacere", "coriandolo"),
        I("80-100 g di fagioli neri interi in scatola (opzionale), sgocciolati", "fagioli neri"),
        I("1-2 peperoncini jalapeño freschi, a rondelle", "jalapeño"),
    ],
    "procedimento": [
        "Mettere nel boccale la farina integrale, l'acqua, 10 g di olio extravergine di oliva e 1 cucchiaino di sale, impostare: Spiga/4 min. Trasferire in una ciotola, coprire con pellicola trasparente e lasciare riposare per 30 minuti. Nel frattempo, continuare con la ricetta. Pulire il boccale.",
        "Mettere nel boccale l'aglio e le cipolle, tritare: 3 sec./vel. 5. Riunire sul fondo con la spatola.",
        "Aggiungere 20 g di olio extravergine di oliva e insaporire: 5 min./120°C/vel. 0.5.",
        "Mettere nel boccale la carne di maiale, la birra, l'acqua, il miele, la paprika affumicata, il cumino, il miso, l'anice stellato, la cannella, lo zucchero e 1 cucchiaino di sale, impostare Cottura lenta/4 h 30 min./98°C. Nel frattempo, dividere l'impasto in 24 pezzi uguali. Su una superficie infarinata, stendere con un matterello 1 pezzo alla volta in un disco (Ø circa 12 cm). Scaldare una padella a fuoco medio e cuocere circa 1 minuto su ciascun lato o fino a quando ben cotte. Trasferire su un piatto e coprire con pellicola trasparente. Tenere da parte fino al momento del bisogno.",
        "Sistemare il recipiente del Varoma sopra una ciotola capiente e svuotare al suo interno il contenuto del boccale, conservando nella ciotola il liquido di cottura e nel recipiente del Varoma la carne.",
        "Mettere nel boccale la carne cotta e tritare: 3-4 sec./vel. 4. Trasferire in una ciotola e tenere da parte.",
        "Prima di servire, scaldare bene una padella antiaderente, immergere ciascun tacos nel liquido di cottura della carne e poi scaldarlo nella padella molto calda a fuoco alto per 8-10 secondi.",
        "Farcire ogni taco con 2-3 cucchiai di carne e servire guarnendo con cipolle rosse, coriandolo, fagioli neri (opzionale) e jalapeño.",
    ],
    "note": [
        "In alternativa è possibile utilizzare il liquido di cottura per ungere la padella prima di passare i tacos.",
        "Servire 4 pezzi a persona o 3 pezzi per una porzione più piccola.",
        "Trascritto da uno screenshot a bassa risoluzione: controllare in particolare velocità 0.5, 98 °C, 24 pezzi e 800 g di spalla.",
    ],
    "passi": [
        P(400, "Pesate nel boccale 400 g di farina integrale.", nota="La ricetta indica 400-450 g: regolate la farina all'impasto."),
        P(290, "Aggiungete 290 g di acqua bollente."),
        P(10, "Aggiungete 10 g di olio extravergine di oliva."),
        T("Aggiungete 1 cucchiaino di sale."),
        R("Impastate.", 240, None, 0, programma="Impastare",
          avvertenza="«Spiga» del Bimby corrisponde al programma Impastare del Connect: durata e velocità le gestisce il programma, non sostituitelo con una velocità manuale. Nella ricetta sono 4 minuti."),
        T("Trasferite l'impasto in una ciotola, copritelo con pellicola trasparente e lasciatelo riposare 30 minuti. Nel frattempo continuate con la ricetta. Pulite il boccale.", attesa_s=1800),
        T("Mettete nel boccale 4 spicchi di aglio."),
        P(150, "Aggiungete 150 g di cipolle, tagliate a metà."),
        R("Tritate.", 3, 5),
        T("Riunite sul fondo con la spatola."),
        P(20, "Pesate nel boccale 20 g di olio extravergine di oliva."),
        R("Insaporite.", 300, 1, 120,
          avvertenza="La ricetta indica velocità 0.5, che sul Connect non c'è: si parte da 1. Se potete, riducete la velocità a quella minima."),
        P(800, "Pesate nel boccale 800 g di spalla di maiale, senza ossa, in 5 pezzi."),
        P(500, "Aggiungete 500 g di birra stout."),
        P(150, "Aggiungete 150 g di acqua."),
        P(70, "Aggiungete 70 g di miele.", nota="La ricetta indica 70-80 g."),
        T("Aggiungete 2 cucchiaini di paprika affumicata, 1 cucchiaino di cumino, 2 cucchiai di miso, 1 bacca di anice stellato, 1 stecca di cannella a metà, 2 cucchiai di zucchero grezzo e 1 cucchiaino di sale."),
        R("Cottura lenta.", 16200, None, 98,
          avvertenza="Cottura lenta del Bimby (4 h 30 min a 98 °C): non è nelle tabelle di conversione. Verificate se il timer del Connect arriva a 4 h 30 e quale velocità usare."),
        T("Nel frattempo dividete l'impasto in 24 pezzi uguali. Su una superficie infarinata stendete con il matterello 1 pezzo alla volta in un disco (Ø circa 12 cm)."),
        T("Scaldate una padella a fuoco medio e cuocete i dischi circa 1 minuto per lato. Trasferite su un piatto e copriteli con pellicola trasparente. Teneteli da parte."),
        T("Sistemate il recipiente del Varoma sopra una ciotola capiente e svuotatevi dentro il contenuto del boccale: il liquido di cottura resta nella ciotola, la carne nel recipiente.",
          avvertenza="Qui il Varoma serve solo da colino. Sul Connect usate un colino capiente o l'accessorio della cottura al vapore."),
        T("Mettete nel boccale la carne cotta."),
        R("Tritate.", 4, 4, avvertenza="La ricetta indica 3-4 secondi: controllate la sfilacciatura."),
        T("Trasferite in una ciotola e tenete da parte."),
        T("Prima di servire scaldate bene una padella antiaderente. Immergete ciascun tacos nel liquido di cottura della carne e scaldatelo nella padella molto calda a fuoco alto per 8-10 secondi."),
        T("Farcite ogni taco con 2-3 cucchiai di carne. Servite guarnendo con 80 g di cipolla rossa tritata, coriandolo, fagioli neri (opzionale) e jalapeño a rondelle."),
    ],
})

out = pathlib.Path(__file__).resolve().parent.parent / "data" / "ricette.json"
out.write_text(json.dumps(ricette, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(ricette)} ricette, {sum(len(r['passi']) for r in ricette)} passi -> {out}")

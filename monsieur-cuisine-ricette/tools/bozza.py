"""Bozza automatica di una ricetta dal testo strutturato di pdf_ricette.py.

  python3 tools/bozza.py LOTTO/rNNNNN/testo.txt [--out ricetta.json]

Scrive il JSON della ricetta (formato di docs/formato-ricetta.md) e stampa una vista compatta dei passi con l'elenco
dei punti da controllare. La bozza non sostituisce la revisione: `importa.py aggiungi` ne esegue comunque il controllo
di coerenza (tools/valida.py). Le regole di traduzione sono quelle di docs/conversione-bimby-connect.md.
"""
import argparse, json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import valida
from valida import ROOT, norm, tokens, grammi, stem

AV05 = "La ricetta indica velocità 0.5, che sul Connect non c'è: si parte da 1. Se potete, usate la velocità minima."
SOFT = "Velocità cucchiaio/Soft del Bimby: velocità 1 con rotazione sinistrorsa."
FRU = "Frullare: partite da velocità bassa e aumentate gradualmente fino alla velocità indicata."
CONF = "Il tempo dipende dalla confezione: controllatelo e impostatelo voi."
VAPORE = ("Varoma del Bimby: sul Connect si usa il programma Cottura al vapore con la vaporiera. Temperatura e velocità le "
          "gestisce il programma: controllate i valori sul display e considerate il preriscaldamento.")
VAROMA_BOCCALE = ("Varoma in una preparazione nel boccale: non sostituirlo in automatico con 120 °C. Il Connect arriva a 130 °C: "
                  "scegliete la temperatura in base alla ricetta.")

UNITA = r"(?:g|ml|kg|l|cucchiaini|cucchiaino|cucchiai|cucchiaio|pizzichi|pizzico|spicchi|spicchio|rametti|rametto|gambi|gambo|foglie|foglia|fette|fetta|mazzetto|mazzetti|filetti|filetto|fili|filo|bacche|bacca|stecca|bustina|costa|coste|ciuffo|ciuffi|baccello|baccelli)"
AGGETTIVI = {"fresco", "fresca", "freschi", "fresche", "maturi", "maturo", "surgelati", "surgelato", "sgusciati", "sgusciato",
             "grattugiato", "grattugiata", "tritato", "tritata", "macinato", "macinata", "pelate", "pelati", "intero", "intera",
             "liquida", "liquido", "nero", "nera"}
VERBI = {  # infinito -> imperativo (voi)
    "Mettere": "Mettete", "Aggiungere": "Aggiungete", "Unire": "Unite", "Versare": "Versate", "Togliere": "Togliete",
    "Trasferire": "Trasferite", "Servire": "Servite", "Riunire": "Riunite", "Lasciare": "Lasciate", "Cuocere": "Cuocete",
    "Tritare": "Tritate", "Tagliare": "Tagliate", "Scaldare": "Scaldate", "Condire": "Condite", "Spolverizzare": "Spolverizzate",
    "Irrorare": "Irrorate", "Sistemare": "Sistemate", "Preriscaldare": "Preriscaldate", "Stendere": "Stendete",
    "Formare": "Formate", "Impastare": "Impastate", "Posizionare": "Posizionate", "Riprendere": "Riprendete",
    "Staccare": "Staccate", "Scolare": "Scolate", "Mescolare": "Mescolate", "Rimuovere": "Rimuovete", "Svuotare": "Svuotate",
    "Attendere": "Attendete", "Controllare": "Controllate", "Aggiustare": "Aggiustate", "Mantecare": "Mantecate",
    "Disporre": "Disponete", "Foderare": "Foderate", "Appoggiare": "Appoggiate", "Pesare": "Pesate", "Pulire": "Pulite",
    "Lavare": "Lavate", "Dividere": "Dividete", "Frullare": "Frullate", "Insaporire": "Insaporite", "Tostare": "Tostate",
    "Sfumare": "Sfumate", "Grattugiare": "Grattugiate", "Amalgamare": "Amalgamate", "Emulsionare": "Emulsionate",
    "Sciogliere": "Sciogliete", "Scottare": "Scottate", "Rosolare": "Rosolate", "Impostare": "Impostate", "Portare": "Portate",
    "Coprire": "Coprite", "Tenere": "Tenete", "Raccogliere": "Raccogliete", "Filtrare": "Filtrate", "Sbucciare": "Sbucciate",
    "Decorare": "Decorate", "Continuare": "Continuate", "Infornare": "Infornate", "Sgocciolare": "Sgocciolate", "Cospargere": "Cospargete", "Unite": "Unite",
}
ADD = re.compile(r"\b(mettere|aggiungere|unire|versare|inserire|incorporare|pesare)\b", re.I)
AZIONE_PRIMA = re.compile(r"\b(trasferire|togliere|servire|riunire|svuotare|rimuovere|scolare)\b", re.I)
CATEGORIE = [("Dessert", r"torta|dolce|budino|gelato|biscott|crostata|muffin|tiramis|marmellata|confettura|panna cotta|mousse"),
             ("Primi", r"risotto|pasta|gnocchi|minestr|zuppa|vellutata|crema di|passato|lasagne|ravioli|spaghetti|tagliatelle|penne|fregola|farro|orzo|orzotto|riso|cous ?cous|bulgur|quinoa|polenta|arroz"),
             ("Secondi", r"polpett|filetto|arrosto|spezzatino|pollo|manzo|maiale|vitello|pesce|merluzzo|salmone|frittata|involtini|hamburger|tacos|uova"),
             ("Contorni", r"contorno|purè|puree|insalata|verdure al|patate al"),
             ("Antipasti", r"antipasto|bruschett|hummus|tartine|sformatini|focaccia|torta salata")]


# ------------------------------------------------------------------ utilità
def vocabolario():
    v = set()
    for f in (ROOT / "data" / "ricette").glob("*.json"):
        v |= set(re.findall(r"[a-zà-ú']+", f.read_text(encoding="utf-8").lower()))
    return v


_VOC2 = set()


def incolla(t, voc):
    t = re.sub(r"\b(cucchiaini|cucchiaino|cucchiai|pizzichi|pizzico|spicchi|rametti)(di)\b", r"\1 \2", t)
    t = re.sub(r"([a-z])(Varoma)\b", r"\1 \2", t)
    t = re.sub(r"\bper l minut", "per 1 minut", t)
    t = re.sub(r"\bg(di|d)(?=[a-zà-ú]{3,})", r"g \1 ", t)
    t = re.sub(r"(\d)g(?=[a-zà-ú]{3,})", r"\1 g ", t)
    """separa le parole attaccate dall'OCR («dilenticchie» → «di lenticchie»), solo se la seconda parte è nota"""
    def f(m):
        w = m.group(0); lw = w.lower()
        if lw in voc: return w
        for pre in ("alle", "agli", "dell", "della", "delle", "nel", "sul", "con", "per", "allo", "ai", "di", "da", "in", "ed", "al", "il", "la", "le", "un", "co", "i"):
            rest_ = lw[len(pre):]
            radici = {stem(x) for x in (voc | _VOC2)} if len(rest_) >= 4 else set()
            if lw.startswith(pre) and len(rest_) >= 4 and (rest_ in voc or rest_ in _VOC2 or stem(rest_) in radici):
                return w[:len(pre)] + " " + w[len(pre):]
        return w
    return re.sub(r"[A-Za-zÀ-ú]+", f, t)


def frazioni(t, dubbi):
    t = re.sub(r"(?<!\d)/2\b", "½", t)
    t = re.sub(r"(\d)\s*/\s*2\b", lambda m: "½" if m.group(1) == "1" else m.group(0), t)
    t = re.sub(r"(?<!\d)/4\b", lambda m: (dubbi.append(f"frazione «/4» in «{t.strip()[:50]}»: ¼ o ¾? verificare sull'immagine"), "¼")[1], t)
    t = re.sub(r"\b1/4\b", "¼", t)
    return t


ACCENTI = [(r"\ba meta\b", "a metà"), (r"\bmeta\b", "metà"), (r"\bpiu\b", "più"), (r"\be possibile\b", "è possibile"), (r"\bfinche\b", "finché"),
           (r"\bvelocita\b", "velocità"), (r"\bcosi\b", "così"), (r"\bpero\b", "però"), (r"\bgia\b", "già"), (r"\bconi\b", "con i"), (r"\bapezzi\b", "a pezzi"), (r"\bat(occhetti|occhetti)\b", r"a t\1"), (r"\bafettine\b", "a fettine"), (r"\bacubetti\b", "a cubetti"), (r"\bmesia\b", "mesi a"), (r"\bper(?=\d)", "per "), (r"\bper(?=brodo)", "per "),
           (r"\b(ceci|fagioli|piselli|lenticchie|pomodori)n\s+scatola", r"\1 in scatola"), (r"\b0,5 [Il1]\b", "0,5 l"), (r"\bincasa\b", "in casa"),
           (r"\bsaporita\b", "saporita"), (r"\bcucina\b", "cucina"), (r"\bquantita\b", "quantità"), (r"\bcosi\b", "così")]


def accenti(t):
    for a, b in ACCENTI:
        t = re.sub(a, b, t)
    return t


def pulisci(t):
    t = re.sub(r"\s*\[\?\d\.\d+\]", "", t).strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s*\(\s*", " (", t).replace(" )", ")").replace("pezzi (", "pezzi (")
    t = re.sub(r"\+\s*q\.b\.?", "+ q.b.", t)
    t = re.sub(r",\s*\(", " (", t)
    t = re.sub(r",\s*,", ",", t)
    return accenti(t.rstrip(","))


def imperativo(t):
    for inf, imp in sorted(VERBI.items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"\b{inf}\b", imp, t)
        t = re.sub(rf"\b{inf.lower()}\b", imp.lower(), t)
    return t


def resto(testo):
    """testo senza la quantità iniziale: «200 g di sedano rapa» -> «sedano rapa»"""
    return re.sub(rf"^[\d½¼¾/\s\-–.,]*(?:{UNITA}\b)?\s*(?:(?:colm[oiae]|ras[oiae]|abbondant[ei])\s+)?(?:di\s+|d')?", "", testo, flags=re.I).strip()


CONTENITORI = r"(?:gambo|gambi|foglie|foglia|foglioline|rametti|rametto|ciuffo|ciuffi|cimette|cimetta|code|testa|teste|spicchio|spicchi|fetta|fette|filetti|filetto|mazzetto|polpa|semi)"


def nome_di(testo):
    r = resto(testo)
    r = re.split(r"[,(]", r)[0].strip().lower()
    r = re.sub(rf"^{CONTENITORI}\s+(?:di\s+|d')?", "", r)
    r = re.split(r"\s+(?:a|da|per|con|in|tipo)\s+", r)[0]
    parole = [p for p in r.split() if p not in AGGETTIVI and p not in ("di", "del", "della", "in", "a")]
    return " ".join(parole[:3]) if parole else r


# ------------------------------------------------------------------ lettura del testo strutturato
_VOC = None


def vocabolario_c():
    global _VOC
    if _VOC is None: _VOC = vocabolario()
    return _VOC


def senza_marcatore(r):
    return re.sub(r"^\s*[-=>#]\s+", "", r)


def leggi(path):
    sez, cur = {}, None
    for riga in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if riga.startswith("## "):
            cur = riga[3:].strip(); sez[cur] = []
        elif cur is not None:
            sez[cur].append(riga)
    return sez


def testa(righe, voc):
    righe = [r for r in righe if r.strip() and not re.match(r"^\s*TM\d", r)]
    tit = []
    for r in righe:
        if re.match(r"^\s*Prep", r): break
        tit.append(r.strip())
    t = " ".join(tit)
    righe = [re.sub(r"\b[lI]\s*h\b", "1h", r) for r in righe]
    def ore(pat):
        m = re.search(pat + r"\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*min)?", " ".join(righe))
        return (int(m.group(1) or 0) * 60 + int(m.group(2) or 0)) if m and (m.group(1) or m.group(2)) else None
    porz = re.search(r"(\d+)\s*porzion", " ".join(righe))
    return incolla(t, voc), ore(r"Prep\."), ore(r"Totale"), int(porz.group(1)) if porz else None


def ingredienti(righe, voc, dubbi):
    items, gruppo, ultimo_alt, dopo_hdr = [], None, False, False
    for r in righe:
        if not r.strip(): continue
        if r.startswith(("- ", "# ")): ultimo_alt = False
        if r.startswith("# "):
            gruppo = incolla(pulisci(r[2:]), voc); dopo_hdr = True; continue
        if dopo_hdr and r.startswith("  = "):          # la prima voce sotto un titolo di gruppo non è un'alternativa
            r = "- " + r[4:]
        dopo_hdr = False
        testo = incolla(frazioni(pulisci(senza_marcatore(r)), dubbi), voc)
        testo = re.sub(r"^\d\s+(?=\d{2,}\s*g)", "", testo)            # icona di alternativa letta come cifra
        if r.startswith("- ") and items and re.match(r"^\d\s+\d", senza_marcatore(r)):
            items[-1]["alt"].append(testo)
        elif r.startswith("- "):
            items.append({"testo": testo, "gruppo": gruppo, "note": [], "alt": []})
        elif r.startswith("  > ") and items:
            if re.search(r"\[\?0\.[0-7]\d\]", r) and " " not in testo and len(testo) <= 8: continue   # rumore dell'OCR
            if re.fullmatch(r"[A-Za-z]{5,8}", testo) and testo.lower() not in vocabolario_c(): continue
            if ultimo_alt and items[-1]["alt"]: items[-1]["alt"][-1] += " " + testo
            else: items[-1]["note"].append(testo)
        elif r.startswith("  = ") and items:
            items[-1]["alt"].append(testo); ultimo_alt = True
    out = []
    for it in items:
        t = it["testo"]
        for n_ in it["note"]:
            t += (" " if n_.startswith("(") else ", ") + n_
        t = re.sub(r"\s*,\s*\+\s*q\.b\.", " (+ q.b.)", t)
        t = re.sub(r",\s*\(", " (", t).replace("  ", " ")
        d = {"testo": t, "nome": nome_di(it["testo"])}
        al = re.search(r"\(([A-Za-zà-ú]{5,})\)", it["testo"])
        if al: d["_alias"] = al.group(1).lower()
        if it["gruppo"]: d["gruppo"] = it["gruppo"]
        out.append((d, it["alt"]))
    nomi = [d["nome"] for d, _ in out]
    for d, _ in out:                       # nomi duplicati: li lascio uguali, il controllo li somma
        if not d["nome"]: dubbi.append(f"ingrediente senza nome riconoscibile: «{d['testo']}»")
    return out


# ------------------------------------------------------------------ parametri del robot
def norma_vel(t):
    t = re.sub(r"\bvel\.?\s*[oO]([.,]\d)", r"vel. 0\1", t)
    return t


def norma_minuti(t):
    """«20o min.»: la «o» è un residuo se leggerla come zero darebbe più di 150 minuti"""
    return re.sub(r"(\d+)[oO]\s*(?=min\b)", lambda m: (m.group(1) + "0") if int(m.group(1) + "0") < 150 else m.group(1) + " ", t)


def norma_temp(t):
    """«10oc» «1oo'c» «1ooc» «1oo°C» -> «100°C»"""
    def f(m):
        n = m.group(1) + "0" * len(m.group(2))
        if len(n) == 4 and n.endswith("0"): n = n[:3]          # «10ooc»: l'ultima «o» è il simbolo dei gradi
        return n + "°C"
    return re.sub(r"(\d+)([oO]+)\s*[°'`]?\s*[cC]\b", f, norma_minuti(norma_vel(t)))


def parametri(frase, dubbi):
    """estrae tempo, temperatura, velocità, rotazione dalla frase; None se non è un passo robot"""
    f = norma_temp(frase)
    m4 = re.search(r"\b(1[0-3]\d)0\s*°?\s*C\b", f)
    if m4:
        dubbi.append(f"temperatura «{m4.group(1)}0 °C» letta come {m4.group(1)} °C in «{frase[:50]}»")
        f = f.replace(m4.group(0), m4.group(1) + "°C")
    mod = re.search(r"\b(Spiga|Cottura lenta|Sottovuoto|Bollitore|Turbo)\b", f)
    ha_vel = re.search(r"\bvel\b", f)
    fru = re.search(r"\bFrullare\b[^.:]*?(?:/|\s)\s*(\d+\s*(?:min|sec))", f) and not ha_vel
    tm_pat = r"(?:(\d+)\s*h\s*)?(?:(\d+)\s*min\.?\s*)?(?:(\d+)\s*sec\.?)?"
    seg_i = max(f.rfind(":"), 0)
    seg = f[seg_i:] if (ha_vel or fru or mod) else ""
    if not (ha_vel or fru or mod or re.search(r"\d+\s*min\./", f)):
        return None
    h = re.search(r"(\d+)\s*h\b", seg); m = re.search(r"(\d+)\s*(?:-\s*\d+\s*)?min", seg); s = re.search(r"(\d+)\s*(?:-\s*\d+\s*)?sec", seg)
    intervallo = re.search(r"(\d+)\s*-\s*(\d+)\s*(min|sec)", seg)
    qualche = re.search(r"[Qq]ualche\s*sec", f)
    if m and not h and int(m.group(1)) >= 150 and int(m.group(1)) % 10 == 0:
        dubbi.append(f"tempo «{m.group(1)} min» sospetto in «{frase[:60]}»: letto {int(m.group(1)) // 10} min")
        m = re.match(r"(\d+)", str(int(m.group(1)) // 10))
    tempo = (int(h.group(1)) * 3600 if h else 0) + (int(m.group(1)) * 60 if m else 0) + (int(s.group(1)) if s else 0)
    if qualche: tempo = 5
    temp = re.search(r"(\d{2,3})\s*[°'`]?\s*[cC]\b", seg)
    varoma = bool(re.search(r"Varoma", seg))
    rev = bool(re.search(r"//|antiorario", seg))
    v = re.search(r"\bvel\b\.?\s*(?:(\d{1,2}(?:[.,]\d)?)|(cucchiaio)|([.sS])(?=\W|$))", seg)
    vel, cucchiaio = None, False
    if v:
        if v.group(1):
            vel = float(v.group(1).replace(",", "."))
            vel = int(vel) if vel == int(vel) else vel
        else:
            cucchiaio = True
    d = {"tempo_s": tempo or None, "temp_c": int(temp.group(1)) if temp else 0, "velocita": vel, "sinistrorsa": rev,
         "nota": None, "avvertenza": None, "programma": None, "varoma": varoma, "qualche": bool(qualche)}
    if fru:
        d["velocita"] = 10; d["nota"] = FRU
        t = re.search(r"/\s*(?:(\d+)\s*min\.?)?\s*(?:(\d+)\s*sec)?", seg)
    if cucchiaio:
        d["velocita"] = 1; d["sinistrorsa"] = True; d["nota"] = SOFT
    if vel is not None and vel < 1:
        d["velocita"] = 1; d["avvertenza"] = AV05
    if vel is None and not cucchiaio and not fru and not mod:
        dubbi.append(f"velocità non letta in «{frase[:70]}»")
    if mod:
        nm = mod.group(1)
        if nm == "Spiga":
            d["programma"] = "Impastare"; d["velocita"] = None
            d["avvertenza"] = "«Spiga» del Bimby corrisponde al programma Impastare del Connect: durata e velocità le gestisce il programma, non sostituitelo con una velocità manuale."
        else:
            d["avvertenza"] = f"Modalità «{nm}» del Bimby: non è nelle tabelle di conversione. Traduzione al meglio: controllate sul display del Connect come impostarla."
    if intervallo:
        d["nota"] = ((d["nota"] + " ") if d["nota"] else "") + f"La ricetta indica {intervallo.group(1)}-{intervallo.group(2)} {'minuti' if intervallo.group(3) == 'min' else 'secondi'}: il timer è impostato a {intervallo.group(1)}."
    if re.search(r"indicat[oa] sulla confezione", f):
        d["tempo_s"] = None; d["nota"] = ((d["nota"] + " ") if d["nota"] else "") + CONF
    if qualche:
        d["avvertenza"] = "La ricetta dice «qualche secondo»: 5 secondi è indicativo. Controllate il risultato."
    if varoma:
        d["avvertenza"] = VAROMA_BOCCALE
    if re.search(r"senza misurino", f):
        d["nota"] = ((d["nota"] + " ") if d["nota"] else "") + "Senza misurino: lasciate aperto il foro del coperchio, come nella ricetta."
    if re.search(r"\b[Ss]offri", f) and d["temp_c"] and not d["programma"]:
        pass
    return d


PARAMS = re.compile(r"^\s*(?:\d+\s*h\s*)?(?:\d+\s*(?:-\s*\d+\s*)?min\.?\s*)?(?:\d+\s*(?:-\s*\d+\s*)?sec\.?\s*)?(?:/\s*(?:Varoma|\d{2,3}\s*[°'`]?\s*[cC](?:°C)?)\s*)?/*\s*(?:vel\.?\s*(?:\d{1,2}(?:[.,]\d)?|cucchiaio|[.sS])\.?)?")


def etichetta(clausola):
    """verbo del passo robot ricavato dalla frase: «... tritare:» -> «Tritate.»"""
    trovati = [m for m in re.finditer(r"\b(" + "|".join(k.lower() for k in VERBI) + r")\b", clausola.lower())]
    if re.search(r"\bcottura\b", clausola.lower()) and not re.search(r"\b(cuocere|frullare|tostare|insaporire|sfumare)\b", clausola.lower()):
        return "Cuocete."
    azioni = [m for m in trovati if m.group(1) not in ("mettere", "aggiungere", "unire", "versare", "togliere", "trasferire", "tenere", "riunire")]
    if azioni:
        v = azioni[-1].group(1)
        return VERBI[v.capitalize()] + "."
    return "Impostate il robot."


# ------------------------------------------------------------------ passi
def tok_in(tk, cl):
    """tutti i token di tk compaiono in cl (anche come prefisso: pomodori ~ pomodorini)"""
    return bool(tk) and all(t in cl or any(len(t) >= 5 and len(c) >= 5 and (c.startswith(t) or t.startswith(c)) for c in cl) for t in tk)


def stesso_gruppo(a, b):
    import difflib
    if not a or not b: return True
    x, y = norm(a).replace(" ", ""), norm(b).replace(" ", "")
    return x == y or difflib.SequenceMatcher(None, x, y).ratio() >= 0.8


def converti(prep, ingr, voc, dubbi):
    its = [d for d, _ in ingr]
    tk = [tokens(d["nome"]) for d in its]
    resta = [(grammi(d["testo"]) or (0,))[0] for d in its]
    aggiunto = [False] * len(its)
    ult_pes, varoma_ctx = {}, False
    passi, proc, gruppo_att, cur, blocchi = [], [], None, [], []
    for r in prep + [""]:
        if r.startswith("# "):
            gruppo_att = r[2:].strip(); blocchi.append(("G", gruppo_att)); continue
        if r.strip(): cur.append(r.strip())
        elif cur: blocchi.append(("B", " ".join(cur))); cur = []
    gruppi_ing = {d.get("gruppo") for d in its if d.get("gruppo")}
    gruppo = None
    for k_, (tipo, b) in enumerate(blocchi):
        if tipo == "G":
            gruppo = b; continue
        if b.strip() == "[RIGA?]":
            seguente = next((x for t_, x in blocchi[k_ + 1:] if t_ == "B"), "")
            dubbi.append(f"possibile riga mancante nell'OCR prima di «{seguente[:60]}»: verificare con un ritaglio"); continue
        b = re.sub(r"^\d{1,2}\s+(?=[A-ZÀ-Ú])", "", b)               # numero di passo letto dall'OCR
        b = re.sub(r"(?<=\.)\s+\d{1,2}\s+(?=[A-ZÀ-Ú])", " ", b)
        b = incolla(frazioni(pulisci(b), dubbi), voc)
        b = re.sub(r"\b[Ss]ec\s*,\s*/", "sec./", b)
        b = norma_temp(b)
        proc.append((gruppo + ". " if gruppo and gruppi_ing else "") + b)
        frasi = [x for f_ in re.split(r"(?<=\.)\s+(?=[A-ZÀ-Ú])", b) for x in re.split(r",\s+poi\s+(?=\w+\s*:)", f_)]
        for frase in frasi:
            frase = frase.strip()
            if not frase: continue
            par = parametri(frase, dubbi)
            clausola = frase.split(":")[0] if par and ":" in frase else frase
            if re.search(r"recipiente del Varoma|vassoio|[Cc]hiudere il Varoma", frase): varoma_ctx = True
            nel = bool(re.search(r"nel boccale", clausola))
            if par is None and not ADD.search(frase) and not nel and ":" not in frase:
                passi.append(testo_libero(frase)); continue
            in_gruppo = [k for k, d in enumerate(its) if not gruppi_ing or stesso_gruppo(d.get("gruppo"), gruppo)]
            ambito = in_gruppo + [k for k in range(len(its)) if k not in in_gruppo]
            cl_tok, cl_norm = tokens(clausola), norm(clausola)
            pos, vistinomi = [], set()
            for k in ambito:
                n = its[k]["nome"]
                if n in vistinomi: continue
                testa_ = n.split()[0] if n.split() else n
                simili = [m for m in ambito if its[m]["nome"].split()[:1] == [testa_]]
                pieno = tok_in(tk[k], cl_tok) or bool(its[k].get("_alias") and tok_in(tokens(its[k]["_alias"]), cl_tok))
                parziale = len({its[m]["nome"] for m in simili}) == 1 and tok_in(tokens(testa_), cl_tok)
                if pieno or parziale:
                    ts = tk[k] if pieno else tokens(testa_)
                    pos.append((min((m.start() for t in ts for m in re.finditer(t[:4], cl_norm)), default=0), n)); vistinomi.add(n)
            pos.sort()
            primo, extra = True, []
            if ADD.search(clausola) or nel:
                for _, n in pos:
                    cand = [k for k in ambito if its[k]["nome"] == n]
                    cand = [k for k in cand if k in in_gruppo] or cand
                    k = next((k for k in cand if resta[k] > 0), cand[0])
                    it = its[k]
                    g = grammi(it["testo"])
                    esplicito = re.search(r"(\d+(?:[.,]\d+)?)\s*g\s*(?:di|d')?\s*(?:\w+\s+){0,2}?" + re.escape(n.split()[0][:5]), clausola, re.I)
                    quanto = float(esplicito.group(1).replace(",", ".")) if esplicito else None
                    if g and resta[k] > 0:
                        q = quanto if quanto else resta[k]
                        resta[k] -= q; aggiunto[k] = True; ult_pes[k] = len(passi)
                        verbo = "Pesate nel boccale" if primo and nel else ("Pesate" if primo else "Aggiungete")
                        passi.append({"tipo": "pesata", "g": int(q) if q == int(q) else q, "testo": f"{verbo} {q:g} g di {resto(it['testo'])}."})
                        primo = False
                    elif not aggiunto[k] or (g and resta[k] <= 0 and re.search(re.escape(n.split()[0][:4]) + r"\w*\s+restante", clausola)):
                        aggiunto[k] = True
                        extra.append(it["testo"])
                    elif g and ult_pes.get(k) is not None and any("da parte" in (p_.get("testo", "").lower()) for p_ in passi[ult_pes[k]:]):
                        extra.append(f"{n} (messo da parte)")
                if extra:
                    verbo_t = "Mettete nel boccale" if nel and primo else "Aggiungete"
                    passi.append({"tipo": "testo", "testo": f"{verbo_t} " + ", ".join(extra) + "."})
            if par:
                p = {"tipo": "robot", "testo": etichetta(clausola), "tempo_s": par["tempo_s"], "velocita": par["velocita"],
                     "temp_c": par["temp_c"], "sinistrorsa": par["sinistrorsa"]}
                for kk in ("programma", "nota", "avvertenza"):
                    if par[kk]: p[kk] = par[kk]
                if re.search(r"recipiente del Varoma|vassoio|Varoma\s+e\s+sistemare|[Cc]hiudere il Varoma|[Pp]osizionare il Varoma", clausola):
                    varoma_ctx = True
                if par["varoma"]:
                    p["temp_c"] = 0
                    if varoma_ctx:
                        p["programma"] = "Cottura al vapore"; p["avvertenza"] = VAPORE
                passi.append(p)
                resto_frase = frase.split(":", 1)[1] if ":" in frase else ""
                dopo = re.sub(r"senza misurino", "", PARAMS.sub("", resto_frase, count=1)).strip(" .")
                if resto_frase.strip().startswith(",") or re.match(r"^,", dopo) or (dopo[:1].islower() and re.match(r"(?:sempre\s+)?(?:con|senza)\b", dopo)):
                    extra_n = dopo.lstrip(", ").strip()
                    if extra_n:
                        p["nota"] = ((p.get("nota") + " ") if p.get("nota") else "") + extra_n[0].upper() + extra_n[1:].rstrip(".") + "."
                elif len(re.findall(r"[A-Za-zà-ú]{3,}", dopo)) >= 2 and not par["nota"] == FRU:
                    passi.append(testo_libero(dopo))
            elif not (ADD.search(clausola) or nel) or re.search(r"mescol|mantec|amalgam|impast|trasfer|serv|spolver|condir|riunir|togli", frase.lower()):
                passi.append(testo_libero(frase))
    for k, d in enumerate(its):                        # grammi mai pesati: li peso prima del primo passo che li nomina
        if resta[k] > 0:
            for pos_, pz in enumerate(passi):
                if pz["tipo"] == "testo" and (tok_in(tk[k], tokens(pz["testo"])) or tok_in(tokens(d["nome"].split()[0]), tokens(pz["testo"])) or bool(d.get("_alias") and tok_in(tokens(d["_alias"]), tokens(pz["testo"])))):
                    q = resta[k]
                    passi.insert(pos_, {"tipo": "pesata", "g": int(q) if q == int(q) else q, "testo": f"Pesate {q:g} g di {resto(d['testo'])}."})
                    resta[k] = 0; aggiunto[k] = True
                    break
    nomi = [d["nome"] for d in its]
    for d in its:                                      # nome troppo specifico per i passi -> solo la parola principale
        n = d["nome"]
        if tokens(n) and not any(tokens(n) <= tokens(p.get("testo", "")) for p in passi) and len(n.split()) > 1:
            t0 = n.split()[0]
            if any(tokens(t0) <= tokens(p.get("testo", "")) for p in passi) and sum(1 for m in nomi if m.split()[:1] == [t0]) == 1:
                d["nome"] = t0
    nomi = [d["nome"] for d in its]
    nonusati = [n for n in dict.fromkeys(nomi) if tokens(n) and not any(tokens(n) <= tokens(p.get("testo", "")) for p in passi)]
    for n in nonusati:
        dubbi.append(f"ingrediente non trovato nei passi: «{n}»")
    return passi, proc


def testo_libero(frase):
    frase = imperativo(re.sub(r"\s+", " ", frase.strip()))
    d = {"tipo": "testo", "testo": frase}
    m = re.search(r"(?:riposare|attendere|lievitare|raffreddare)[^.]*?(\d+)(?:\s*-\s*\d+)?\s*minut|(?:forno|cuocere)[^.]*?(?:circa|per)\s*(\d+)(?:\s*-\s*\d+)?\s*minut", frase, re.I)
    if m:
        d["attesa_s"] = int(m.group(1) or m.group(2)) * 60
    return d


# ------------------------------------------------------------------ ricetta
def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", norm(t)).strip("-")[:60]


def bozza(path, origine=None):
    voc = vocabolario()
    sez = leggi(path)
    global _VOC2
    _VOC2 = set(re.findall(r"[a-zà-ú']+", " ".join(sez.get("INGREDIENTI", []) + sez.get("TESTA", [])).lower()))     # parole della ricetta stessa
    dubbi = []
    titolo, prep_m, tot_m, porz = testa(sez.get("TESTA", []), voc)
    ingr = ingredienti(sez.get("INGREDIENTI", []), voc, dubbi)
    passi, proc = converti(sez.get("PREPARAZIONE", []), ingr, voc, dubbi)
    meta = dict(r.split(": ", 1) for r in sez.get("META", []) if ": " in r)
    cat, dedotto = "NA", []
    for c, pat in CATEGORIE:
        if re.search(pat, titolo.lower()):
            cat, dedotto = c, ["categoria"]; break
    if cat == "NA": dubbi.append("categoria non deducibile: NA")
    note = [pulisci(incolla(r.strip().lstrip("•:- "), voc)) for r in sez.get("CONSIGLI", []) if r.strip()]
    for _, alt in ingr:
        for a in alt: note.append("In alternativa: " + a)
    if note: pass
    pae = meta.get("paese", "NA")
    if len(pae) < 4: pae = "NA"
    for pat, paese_ in ((r"messican|tacos|burrito|nachos|guacamole|arroz", "Messico"), (r"giappones|sushi|ramen", "Giappone"),
                        (r"indian|curry|tikka", "India"), (r"greco|greca|moussaka", "Grecia"), (r"francese|ratatouille", "Francia")):
        if re.search(pat, titolo.lower()) and pae != paese_:
            dubbi.append(f"paese «{pae}» dalla fonte, ma il titolo indica {paese_}: usato {paese_} (dedotto)")
            pae = paese_; dedotto.append("paese"); break
    dif = meta.get("difficolta", "NA").capitalize() if meta.get("difficolta") else "NA"
    r = {"id": slug(titolo), "titolo": titolo, "categoria": cat, "paese": pae, "dedotto": dedotto,
         "tempo_prep_min": prep_m, "tempo_cottura_min": None, "tempo_min": tot_m, "porzioni": porz, "difficolta": dif,
         "fonte": "Cookidoo (Vorwerk)", "immagine": None, "ingredienti": [{k: v for k, v in d.items() if not k.startswith("_")} for d, _ in ingr], "procedimento": proc,
         "note": note, "passi": passi}
    if origine: r["origine"] = origine
    if pae not in ("NA", "Italia"): dubbi.append(f"paese dalla fonte: «{pae}» (controllare se plausibile)")
    return r, dubbi


def vista(r, dubbi):
    L = [f"== {r['titolo']}  [{r['id']}]  {r['categoria']}  prep {r['tempo_prep_min']} / tot {r['tempo_min']} min  {r['porzioni']} porz  {r['difficolta']}  {r['paese']}"]
    for i, p in enumerate(r["passi"], 1):
        if p["tipo"] == "pesata": L.append(f"{i:2d} P {p['g']:g} g  {p['testo'][:78]}")
        elif p["tipo"] == "testo": L.append(f"{i:2d} T {'⏱' + str(p['attesa_s']) + 's ' if p.get('attesa_s') else ''}{p['testo'][:84]}")
        else:
            t = p["tempo_s"]; tt = f"{t // 60:02d}:{t % 60:02d}" if t else "--:--"
            L.append(f"{i:2d} R {tt} v{p['velocita']} {p['temp_c']}°C{' ⟲' if p['sinistrorsa'] else ''}{' ['+p['programma']+']' if p.get('programma') else ''}{' ⚠' if p.get('avvertenza') else ''}  {p['testo']}")
    E, W = valida.valida(r, valida.carica_tutte())
    L += [f"ERRORE: {e}" for e in E] + [f"avviso: {w}" for w in W if w != "nessuna foto"] + [f"DUBBIO: {d}" for d in dubbi]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("testo"); ap.add_argument("--out"); ap.add_argument("--origine")
    a = ap.parse_args()
    origine = a.origine or ("cookidoo:" + pathlib.Path(a.testo).resolve().parent.name if re.match(r"r\d+$", pathlib.Path(a.testo).resolve().parent.name) else None)
    r, dubbi = bozza(a.testo, origine)
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(vista(r, dubbi))


if __name__ == "__main__":
    main()

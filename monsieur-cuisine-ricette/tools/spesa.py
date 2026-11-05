"""Dati per la lista della spesa: da ogni riga di ingrediente ricava nome unico, quantità, unità, reparto e regola «da casa».

  python3 tools/spesa.py            # rapporto: voci senza reparto, unità, regole applicate

Non modifica le ricette: build.py chiama `spesa_ricetta()` e incorpora il risultato nell'app.
Le regole stanno in questo file (ALIAS, REPARTI, DA_CASA): per cambiare soglie o reparti basta modificarle qui.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- reparti (ordine di visualizzazione)
REPARTI = ["Frutta e verdura", "Erbe e spezie", "Carne, pesce e salumi", "Latticini e uova",
           "Pane, pasta e cereali", "Dispensa", "Altro"]

# ---------------------------------------------------------------- «da casa»
# mai in lista, qualunque quantità
MAI = {"sale", "pepe", "acqua", "ghiaccio"}
# in lista solo se il totale (in grammi) supera la soglia
SOGLIA_G = {"olio extravergine di oliva": 200, "zucchero": 200, "farina": 200, "aceto": 200}

# ---------------------------------------------------------------- nomi unici: (regex sul nome del JSON, nome unico)
ALIAS = [
    (r"^acqua", "acqua"), (r"^ghiaccio", "ghiaccio"),
    (r"^sale", "sale"), (r"^pepe (nero|bianco)$|^pepe$", "pepe"), (r"^pepe cayenna", "pepe di Cayenna"),
    (r"^olio extravergine", "olio extravergine di oliva"), (r"^olio semi mais", "olio di semi di mais"), (r"^olio sesamo", "olio di sesamo"),
    (r"^aceto", "aceto"),
    (r"^zucchero", "zucchero"), (r"^farina", "farina"), (r"^amido", "amido di mais"),
    (r"^cipolla rossa|^cipolle rosse", "cipolla rossa"), (r"^cipollott", "cipollotti"), (r"^cipoll", "cipolla"),
    (r"^scalogno", "scalogno"), (r"^aglio in polvere", "aglio in polvere"), (r"^aglio", "aglio"),
    (r"^carot", "carote"), (r"^patate (americane )?dolci|^patate americane", "patate dolci"), (r"^patat", "patate"),
    (r"^porr", "porri"), (r"^sedano rapa", "sedano rapa"), (r"^sedano", "sedano"),
    (r"^pomodori pelati|^polpa pomodoro", "pomodori pelati"), (r"^passata", "passata di pomodoro"),
    (r"^concentrato", "concentrato di pomodoro"), (r"^pomodori secchi", "pomodori secchi"),
    (r"^pomodor", "pomodori"),
    (r"^succo (limone|lime)", None),   # sotto
    (r"^scorza", "scorza di limone"), (r"^limon", "limoni"),
    (r"^cavolo verza|^verza|^verze", "cavolo verza"), (r"^cavolo (cappuccio )?rosso", "cavolo rosso"),
    (r"^cavolo cappuccio", "cavolo cappuccio"), (r"^cavolo riccio", "cavolo riccio"), (r"^cavolfiore", "cavolfiore"),
    (r"^cavoletti", "cavoletti di Bruxelles"), (r"^cavolo", "cavolo"),
    (r"^broccol|^cimette di broccol", "broccoli"),
    (r"^zucchin", "zucchine"), (r"^zucca", "zucca"), (r"^melanzan", "melanzane"),
    (r"^peperoncino secco|^peperoncini secchi", "peperoncino secco"), (r"^peperoncin", "peperoncino"), (r"^peperon", "peperoni"),
    (r"^spinaci", "spinaci"), (r"^piselli|^baccelli", "piselli"), (r"^fagiolini", "fagiolini"),
    (r"^ceci", "ceci"), (r"^lenticchie rosse", "lenticchie rosse"), (r"^lenticchie", "lenticchie"),
    (r"^fagioli (bianchi|cannellini)", "fagioli cannellini"), (r"^fagioli", None),
    (r"^gamber|^gambero", "gamberi"),
    (r"^parmigiano", "parmigiano reggiano"),
    (r"^uova|^uovo", "uova"), (r"^tuorl", "tuorli"),
    (r"^panna soia", "panna di soia"), (r"^panna", "panna"),
    (r"^latte cocco|^latte di cocco", "latte di cocco"),
    (r"^dado|^dadi", "dado"),
    (r"^brodo vegetale", "brodo vegetale"),
    (r"^pasta curry", "pasta di curry rosso"),
    (r"^pasta integrale", "pasta integrale"), (r"^fregola", "fregola"), (r"^spaghetti", "spaghetti"),
    (r"^pasta|^penne|^caserecce|^casarecce", "pasta secca corta"),
    (r"^riso basmati", "riso basmati"), (r"^riso", "riso"),
    (r"^pane carasau", "pane carasau"), (r"^pane integrale", "pane integrale"), (r"^pane|^crostini", "pane"),
    (r"^salvia", "salvia"), (r"^menta", "menta"),
    (r"^coriandolo", "coriandolo fresco"), (r"^semi (di )?coriandolo", "semi di coriandolo"), (r"^semi (di )?cumino", "semi di cumino"),
    (r"^paprica|^paprika", "paprica dolce"), (r"^cannella|^stecca cannella", "cannella"),
    (r"^funghi porcini secchi|^polvere funghi", "funghi porcini secchi"),
    (r"^nocciole", "nocciole"), (r"^salsiccia", "salsiccia"), (r"^pancetta", "pancetta"),
    (r"^vino bianco", "vino bianco"), (r"^limone", "limoni"),
    (r"^tonno|^filetti di tonno", "tonno"), (r"^sesamo|^semi di sesamo", "semi di sesamo"),
    (r"^ricotta salata", "ricotta salata"), (r"^ricotta", "ricotta"),
    (r"^scamorza", "scamorza"), (r"^mele$", "mele"), (r"^pere", "pere"),
    (r"^finocchietto", "finocchietto selvatico"), (r"^erba cipollina", "erba cipollina"),
    (r"^acciuga", "acciughe sott'olio"), (r"^arachidi", "arachidi"),
    (r"^vegetariano", "macinato vegetariano"), (r"^misto", "misto per soffritto"),
]
ALIAS_C = [(re.compile(p), c) for p, c in ALIAS]

# ---------------------------------------------------------------- reparto per parola chiave sul nome unico (prima corrispondenza)
REP_KW = [   # parole che INIZIANO con la chiave (ancorate con \b: «menta» non cade più in «emmental»); vince la prima regola
    ("Carne, pesce e salumi", r"acciughe"),
    ("Dispensa", r"brodo|dado|salsa|olio|aceto|vino|birra|cognac|passata|pelati|concentrato|funghi .*secchi|pomodori secchi|pasta di|panna di soia|burro di|crema|ceci|fagioli\b|lenticchie|fave|mais dolce|zucchero|miele|sciroppo|miso|olive|nocciole|pinoli|arachidi|anacardi|uvetta|chips|caffe|macinato"),
    ("Erbe e spezie", r"prezzemolo|basilico|rosmarino|timo|salvia|menta|alloro|origano|coriandolo|erba cipollina|finocchietto|zafferano|curcuma|curry|cumino|paprica|noce moscata|cannella|cardamomo|chiodi|anice|ginepro|zenzero|peperoncino|pepe di|lemon grass|odori|tabasco|mix spezie|semi di|aglio in polvere"),
    ("Carne, pesce e salumi", r"acciughe|carne|vitello|filetto|spalla|maiale|pollo|petto|salsiccia|pancetta|guanciale|prosciutto|speck|salame|ossa|gamberi|tonno|acciughe|seppioline|vongole|molluschi|stoccafisso"),
    ("Latticini e uova", r"uova|tuorli|latte|panna|burro|burrata|mascarpone|ricotta|parmigiano|pecorino|emmental|gorgonzola|feta|cheddar|scamorza|stracchino|stracciatella|formaggio"),
    ("Pane, pasta e cereali", r"pasta|spaghetti|fregola|riso|pane|crostini|farro|bulgur|cous cous|quinoa|miglio|cereali|amido|farina"),
    ("Frutta e verdura", r"cipoll|scalogno|aglio|carote|patate|porri|sedano|pomodori|limon|scorza|succo|cavol|broccol|zucchin|zucca|melanzan|peperon|spinaci|piselli|fagiolini|lattuga|cetriolo|mele|pere|cachi|barbabietola|finocch|funghi|jalape|verdure|albicocche|misto|uva"),
]
REP_C = [(r, re.compile(r"\b(?:" + p + ")")) for r, p in REP_KW]

# ---------------------------------------------------------------- unità
UNITA = {
    "g": ("g", 1), "kg": ("g", 1000), "ml": ("ml", 1), "l": ("ml", 1000),
    "cucchiaino": ("cucchiaino", 1), "cucchiaini": ("cucchiaino", 1), "cucchiaio": ("cucchiaio", 1), "cucchiai": ("cucchiaio", 1),
    "pizzico": ("pizzico", 1), "pizzichi": ("pizzico", 1), "spicchio": ("spicchio", 1), "spicchi": ("spicchio", 1),
    "rametto": ("rametto", 1), "rametti": ("rametto", 1), "mazzetto": ("mazzetto", 1), "mazzetti": ("mazzetto", 1),
    "foglia": ("foglia", 1), "foglie": ("foglia", 1), "fetta": ("fetta", 1), "fette": ("fetta", 1), "stecca": ("stecca", 1),
    "gambo": ("gambo", 1), "gambi": ("gambo", 1), "costa": ("costa", 1), "coste": ("costa", 1), "ciuffo": ("ciuffo", 1), "ciuffi": ("ciuffo", 1),
    "bustina": ("bustina", 1), "bustine": ("bustina", 1), "gocce": ("goccia", 1),
}
FRAZ = {"¼": .25, "½": .5, "¾": .75, "⅓": 1 / 3, "⅔": 2 / 3}


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def nome_unico(nome, testo):
    n = norm(nome)
    for rx, c in ALIAS_C:
        if rx.search(n):
            if c is not None:
                return c
            if n.startswith("succo"):
                return "succo di limone" if "limone" in n else "succo di lime"
            if n.startswith("fagioli"):
                return n
    return n


def quantita(testo):
    """-> (numero|None, unità|None). Intervalli: si prende il massimo. Frazioni ¼ ½ ¾ e «1 ½»."""
    t = testo.strip().lower()
    m = re.match(r"^((?:\d+(?:[.,]\d+)?)?\s*[¼½¾⅓⅔]?|\d+(?:[.,]\d+)?)(?:\s*-\s*((?:\d+(?:[.,]\d+)?)?\s*[¼½¾⅓⅔]?))?\s*", t)
    if not m or not m.group(1).strip():
        return None, None
    def val(s):
        s = s.strip()
        if not s: return None
        tot = 0.0
        for p in re.findall(r"\d+(?:[.,]\d+)?|[¼½¾⅓⅔]", s):
            tot += FRAZ[p] if p in FRAZ else float(p.replace(",", "."))
        return tot
    a, b = val(m.group(1)), val(m.group(2) or "")
    q = max(x for x in (a, b) if x is not None)
    resto = t[m.end():]
    u = re.match(r"([a-zà-ù]+)", resto)
    if u and u.group(1) in UNITA:
        un, mult = UNITA[u.group(1)]
        return q * mult, un
    return q, "pz"


def reparto(c):
    for r, rx in REP_C:
        if rx.search(c):
            return r
    return "Altro"


def spesa_ricetta(r):
    """Voci della lista per UNA ricetta (alle sue porzioni): [{c, q, u, r}]."""
    out = []
    for i in r["ingredienti"]:
        c = nome_unico(i["nome"], i["testo"])
        q, u = quantita(i["testo"])
        if q is not None and u == "pz" and re.match(r"^\d+(?:[.,]\d+)?\s*(?:-\s*\d+)?\s*(?:g|ml)\b", i["testo"].lower()):
            q, u = None, None
        out.append({"c": c, "q": None if q is None else round(q, 2), "u": u, "r": reparto(c)})
    return out


def regole():
    return {"reparti": REPARTI, "mai": sorted(MAI), "soglia_g": SOGLIA_G}


def main():
    import collections
    senza, unit, tot, righe = collections.Counter(), collections.Counter(), 0, 0
    for f in sorted((ROOT / "data" / "ricette").glob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        for v, i in zip(spesa_ricetta(r), r["ingredienti"]):
            righe += 1; unit[v["u"]] += 1
            if v["r"] == "Altro": senza[(v["c"], i["testo"][:40])] += 1
    print(f"{righe} righe di ingredienti")
    print("unità:", dict(unit))
    print(f"\nvoci finite in «Altro» ({len(senza)}):")
    for (c, t), n in sorted(senza.items()): print(f"  {c!r:34} {t}")


if __name__ == "__main__":
    main()

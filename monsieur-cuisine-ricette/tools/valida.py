"""Controllo di coerenza delle ricette (data/ricette/*.json).

Un ERRORE blocca l'importazione (la ricetta va in import/failed/).
Un AVVISO non la blocca: finisce nel riepilogo da rivedere.

Uso: python3 tools/valida.py [id ...]     (senza argomenti controlla tutte le ricette)
"""
import json, pathlib, re, sys, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIE = {"Antipasti", "Primi", "Secondi", "Contorni", "Dessert", "Conserve", "Creme", "NA"}
CAMPI_DEDUCIBILI = {"categoria", "paese", "difficolta", "tempo_min", "porzioni"}
PROGRAMMI_CONNECT = {"Rosolare", "Impastare", "Cottura al vapore"}
VEL_MIN, VEL_MAX, TEMP_MAX = 1, 10, 130          # limiti del Connect


def norm(s):
    return unicodedata.normalize("NFD", str(s).lower()).encode("ascii", "ignore").decode()


def stem(w):
    return w[:-1] if len(w) >= 4 and w[-1] in "aeio" else w


def tokens(s):
    return {stem(t) for t in re.findall(r"[a-z]+", norm(s)) if len(t) > 2}


def grammi(testo):
    """(min, max) di grammi se la riga inizia con una quantità in g, altrimenti None."""
    m = re.match(r"\s*(\d+(?:[.,]\d+)?)(?:\s*-\s*(\d+(?:[.,]\d+)?))?\s*g\b", testo)
    if not m:
        return None
    a = float(m.group(1).replace(",", "."))
    b = float(m.group(2).replace(",", ".")) if m.group(2) else a
    return a, b


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def valida(r, altre=()):
    """Restituisce (errori, avvisi) per una ricetta (dict). `altre` = le altre ricette già presenti."""
    E, W = [], []
    rid = r.get("id", "?")

    # ---- struttura
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(r.get("id", ""))):
        E.append("id mancante o non valido (solo minuscole, numeri e trattini)")
    for k in ("titolo", "categoria", "paese", "difficolta"):
        if not isinstance(r.get(k), str) or not r[k].strip():
            E.append(f"campo «{k}» mancante (usare \"NA\" se non ricavabile)")
    if r.get("categoria") not in CATEGORIE and isinstance(r.get("categoria"), str):
        W.append(f"categoria «{r['categoria']}» non è tra quelle usuali: {', '.join(sorted(CATEGORIE - {'NA'}))}")
    if not isinstance(r.get("dedotto", []), list) or not set(r.get("dedotto", [])) <= CAMPI_DEDUCIBILI:
        E.append(f"«dedotto» deve elencare solo campi tra {sorted(CAMPI_DEDUCIBILI)}")
    for k in ("tempo_min", "porzioni"):
        v = r.get(k)
        if v is not None and not (isinstance(v, int) and v > 0):
            E.append(f"«{k}» deve essere un intero positivo o null")
    if not r.get("ingredienti"):
        E.append("nessun ingrediente")
    if not r.get("procedimento"):
        E.append("procedimento generale mancante")
    if not r.get("passi"):
        E.append("nessun passo")
    img = r.get("immagine")
    if img is not None and not (ROOT / "data" / "img" / img).exists():
        E.append(f"immagine «{img}» non trovata in data/img/")
    if img is None:
        W.append("nessuna foto")
    for a in altre:
        if a.get("id") == r.get("id"):
            E.append(f"duplicato: esiste già una ricetta con id «{rid}»")
        elif r.get("origine") and a.get("origine") == r.get("origine"):
            E.append(f"duplicato: «{r['origine']}» è già stata importata come «{a['titolo']}» ({a.get('id')})")
        elif norm(a.get("titolo", "")) == norm(r.get("titolo", "")):
            E.append(f"duplicato: esiste già una ricetta intitolata «{a['titolo']}» ({a.get('id')})")
    if E and not r.get("ingredienti") or not r.get("passi"):
        return E, W

    ing = r["ingredienti"]
    for i, x in enumerate(ing, 1):
        if not x.get("testo") or not x.get("nome"):
            E.append(f"ingrediente {i}: servono «testo» e «nome»")
    if any(not x.get("testo") or not x.get("nome") for x in ing):
        return E, W

    # ---- passi
    pesate = []
    t_robot = t_attesa = 0
    for n, p in enumerate(r["passi"], 1):
        t = p.get("tipo")
        if t not in ("pesata", "testo", "robot"):
            E.append(f"passo {n}: tipo «{t}» non valido"); continue
        if not isinstance(p.get("testo"), str) or not p["testo"].strip():
            E.append(f"passo {n}: testo vuoto")
        if t == "pesata":
            if not (_num(p.get("g")) and p["g"] > 0):
                E.append(f"passo {n}: «g» deve essere un numero positivo")
            else:
                pesate.append((n, p))
        if t == "robot":
            v, tm, tc = p.get("velocita"), p.get("tempo_s"), p.get("temp_c")
            if v is not None and not (_num(v) and VEL_MIN <= v <= VEL_MAX and v == int(v)):
                E.append(f"passo {n}: velocità {v} fuori dai limiti del Connect ({VEL_MIN}-{VEL_MAX}, solo valori interi)")
            if tc is None or not (_num(tc) and 0 <= tc <= TEMP_MAX):
                E.append(f"passo {n}: temperatura {tc} fuori dai limiti del Connect (0-{TEMP_MAX} °C)")
            if tm is not None and not (isinstance(tm, int) and tm > 0):
                E.append(f"passo {n}: «tempo_s» deve essere un intero positivo o null")
            if not isinstance(p.get("sinistrorsa", False), bool):
                E.append(f"passo {n}: «sinistrorsa» deve essere true/false")
            if tm is None and not (p.get("nota") or p.get("avvertenza")):
                W.append(f"passo {n}: tempo mancante senza nota che lo spieghi")
            if v is None and not (p.get("avvertenza") or p.get("programma")):
                W.append(f"passo {n}: velocità mancante senza avvertenza")
            if p.get("programma") and p["programma"] not in PROGRAMMI_CONNECT:
                W.append(f"passo {n}: programma «{p['programma']}» non è tra quelli del Connect {sorted(PROGRAMMI_CONNECT)}")
            if p.get("accessorio") not in (None, "lame", "emulsionatore"):
                E.append(f"passo {n}: accessorio «{p['accessorio']}» non valido (lame|emulsionatore)")
            t_robot += tm or 0
        if p.get("attesa_s"):
            if not (isinstance(p["attesa_s"], int) and p["attesa_s"] > 0):
                E.append(f"passo {n}: «attesa_s» deve essere un intero positivo")
            else:
                t_attesa += p["attesa_s"]

    # ---- coerenza numeri: pesate <-> ingredienti
    nomi = {x["nome"]: tokens(x["nome"]) for x in ing}
    attese = {}                       # nome -> grammi pesati
    for n, p in pesate:
        tp = tokens(p["testo"])
        cand = [k for k, tk in nomi.items() if tk and tk <= tp]
        if not cand:
            E.append(f"passo {n}: pesata di {p['g']:g} g senza ingrediente corrispondente ({p['testo']})")
            continue
        ordine = [stem(t) for t in re.findall(r"[a-z]+", norm(p["testo"]))]
        # più specifico (più parole) vince; a parità, quello nominato per primo nel testo
        k = max(cand, key=lambda c: (len(nomi[c]), -min(ordine.index(t) for t in nomi[c])))
        attese[k] = attese.get(k, 0) + p["g"]

    testi = [tokens(p["testo"]) for p in r["passi"]]
    for k in nomi:
        g = [grammi(x["testo"]) for x in ing if x["nome"] == k]
        g = [x for x in g if x]
        if k in attese:
            if not g:
                W.append(f"«{k}»: pesato {attese[k]:g} g ma nessuna quantità in g tra gli ingredienti")
                continue
            lo, hi = sum(a for a, _ in g), sum(b for _, b in g)
            if not (lo - 1e-9 <= attese[k] <= hi + 1e-9):
                intervallo = f"{lo:g}" if lo == hi else f"{lo:g}-{hi:g}"
                E.append(f"«{k}»: negli ingredienti {intervallo} g, ma nei passi se ne pesano {attese[k]:g} g")
        elif not any(nomi[k] <= tt for tt in testi):
            E.append(f"«{k}»: ingrediente mai usato nei passi")
        elif g:
            lo, hi = sum(a for a, _ in g), sum(b for _, b in g)
            W.append(f"«{k}»: {lo:g}{'' if lo == hi else f'-{hi:g}'} g non pesati sulla bilancia (usati solo nel testo)")

    # ---- tempi
    if r.get("tempo_min") and (t_robot + t_attesa) / 60 > r["tempo_min"] * 1.15 + 1:
        W.append(f"i tempi dei passi ({(t_robot + t_attesa) / 60:.0f} min) superano il tempo totale indicato ({r['tempo_min']} min)")
    return E, W


def carica_tutte():
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "data" / "ricette").glob("*.json"))]


def main(argv):
    tutte = carica_tutte()
    scelte = [r for r in tutte if not argv or r["id"] in argv]
    if argv and len(scelte) != len(set(argv)):
        print("ricetta non trovata:", set(argv) - {r["id"] for r in scelte}); return 2
    ko = 0
    for r in scelte:
        E, W = valida(r, [a for a in tutte if a is not r])
        stato = "ERRORI" if E else ("ok con avvisi" if W else "ok")
        print(f"{r['id']}: {stato}")
        for e in E: print("  ERRORE ", e)
        for w in W: print("  avviso ", w)
        ko += bool(E)
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

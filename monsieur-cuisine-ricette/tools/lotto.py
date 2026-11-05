"""Importa un lotto di PDF Cookidoo con UN solo comando.

  python3 tools/lotto.py FILE1.pdf FILE2.pdf ... [--no-git]

Per ogni ricetta: estrazione (OCR locale) -> bozza -> controllo di coerenza.
  - pulita (nessun errore, nessun dubbio rilevante): importata subito;
  - da rivedere (errori o dubbi): NON importata; si stampa solo la sua vista compatta e il JSON
    di bozza resta in <lavoro>/<codice>.json, da correggere e importare con `importa.py aggiungi`.
Alla fine ricostruisce l'app, fa commit e push (salvo --no-git) e stampa il riepilogo.
Resta fuori solo la pubblicazione dell'artifact (la fa Claude con lo strumento Artifact).
"""
import argparse, json, pathlib, re, subprocess, sys, tempfile

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import bozza as B, valida, pdf_ricette

ROOT = valida.ROOT
LIEVI = ("paese dalla fonte", "paese «")         # dubbi che non bloccano l'importazione automatica


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="+"); ap.add_argument("--lavoro"); ap.add_argument("--no-git", action="store_true")
    a = ap.parse_args()
    lavoro = pathlib.Path(a.lavoro or tempfile.mkdtemp(prefix="lotto-")); lavoro.mkdir(parents=True, exist_ok=True)

    pdf_ricette.estrai(argparse.Namespace(pdf=a.pdf, out=str(lavoro), foto_box=None))
    codici = sorted(d.name for d in lavoro.iterdir() if d.is_dir())
    ok, rivedere = [], []
    for c in codici:
        try:
            r, dubbi = B.bozza(str(lavoro / c / "testo.txt"), "cookidoo:" + c)
        except Exception as e:
            rivedere.append((c, f"== {c}: bozza fallita ({type(e).__name__}: {e})")); continue
        (lavoro / f"{c}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        E, _ = valida.valida(dict(r, immagine=None), valida.carica_tutte())
        gravi = [d for d in dubbi if not d.startswith(LIEVI) and not d.startswith("categoria non deducibile")]
        if E or gravi:
            rivedere.append((c, B.vista(r, dubbi))); continue
        p = subprocess.run([sys.executable, str(AQUI / "importa.py"), "aggiungi", str(lavoro / f"{c}.json"),
                            "--foto", str(lavoro / c / "foto.jpg")], capture_output=True, text=True)
        if p.returncode:
            rivedere.append((c, B.vista(r, dubbi) + "\n" + p.stdout.strip()))
        else:
            extra = [l.strip() for l in p.stdout.splitlines() if l.startswith("  ") and "avviso" not in l]
            ok.append((r["titolo"], len(r["passi"]), extra))

    print(f"\n===== IMPORTATE {len(ok)} / {len(codici)} =====")
    for t, n, extra in ok:
        print(f"- {t} ({n} passi)" + ("".join(f"\n    {x}" for x in extra)))
    if rivedere:
        print(f"\n===== DA RIVEDERE {len(rivedere)} (bozze in {lavoro}/<codice>.json, foto in {lavoro}/<codice>/) =====")
        for _, v in rivedere: print(v + "\n")
    totale = len(list((ROOT / "data" / "ricette").glob("*.json")))
    print(f"\nRicette nell'app: {totale}. Resta: pubblicare dist/index.html sull'artifact" + (" e rivedere le ricette sopra." if rivedere else "."))
    if ok and not a.no_git:
        subprocess.run(["git", "add", "-A"], cwd=ROOT.parent)
        subprocess.run(["git", "commit", "-q", "-m", f"Importate {len(ok)} ricette (lotto)"], cwd=ROOT.parent)
        subprocess.run(["git", "push", "-q", "origin", "HEAD"], cwd=ROOT.parent)
    return 0


if __name__ == "__main__":
    sys.exit(main())

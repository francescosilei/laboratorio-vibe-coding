#!/usr/bin/env python3
"""Divide una registrazione di una sezione in tante frasi, separate da silenzi lunghi.

Uso:  python3 dividi_audio.py FILE_AUDIO CODICE_SEZIONE [CARTELLA_USCITA] [--pausa=SECONDI]
Esempio: python3 dividi_audio.py A_parole-guida.m4a A_parole-guida audio/ --pausa=0.8
(--pausa = silenzio minimo che separa due pezzi; 3 secondi se omessa)

Passi: trova i silenzi lunghi (almeno 3 s, con soglia adattata al rumore di fondo), taglia le
frasi con un piccolo margine, uniforma il volume con un unico guadagno per tutto il file e
salva ogni frase in MP3 mono 96 kbit/s
con il nome previsto da nomi-registrazioni.json. Se il numero di frasi trovate non
coincide con quello atteso, non scrive nulla e lo dice.
"""
import json, os, subprocess, sys, tempfile
import numpy as np

FRAZIONI = [0.25, 0.35, 0.18, 0.5, 0.12, 0.6, 0.7, 0.8]  # soglia = rumore + frazione*(voce - rumore), dalla più usuale
SILENZIO_MIN = 3.0                              # secondi di silenzio che separano due frasi (opzione --pausa)
MARGINE = 0.20                                  # secondi di margine tenuti attorno alla frase
OBIETTIVO_DB = -20.0                            # volume tipico del parlato (dBFS) dopo l'elaborazione
FINESTRA = 0.05                                 # secondi per ogni misura di volume


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def livelli(path):
    """Volume (in dB) ogni 50 ms."""
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                       capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.float32)
    n = int(16000 * FINESTRA)
    x = x[: len(x) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((x ** 2).mean(axis=1)) + 1e-9)


def frasi(db, frazione, pausa):
    rumore, voce = max(np.percentile(db, 10), -70.0), np.percentile(db, 95)   # alcune app registrano silenzio digitale (-180 dB)
    attivo = db > rumore + frazione * (voce - rumore)
    tratti, i = [], 0
    while i < len(attivo):
        if attivo[i]:
            j = i
            while j < len(attivo) and attivo[j]:
                j += 1
            tratti.append([i, j])
            i = j
        else:
            i += 1
    unite = []
    for t in tratti:                      # unisce i tratti separati da pause brevi (dentro la stessa frase)
        if unite and (t[0] - unite[-1][1]) * FINESTRA < pausa:
            unite[-1][1] = t[1]
        else:
            unite.append(t)
    return [(a * FINESTRA, b * FINESTRA) for a, b in unite if (b - a) * FINESTRA >= 0.3]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--pausa=")]
    pausa = SILENZIO_MIN
    for a in sys.argv[1:]:
        if a.startswith("--pausa="):
            pausa = float(a.split("=")[1])
    if len(args) < 2:
        sys.exit(__doc__)
    src, sezione = args[0], args[1]
    out = args[2] if len(args) > 2 else "audio"
    nomi = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "nomi-registrazioni.json")))[sezione]
    with tempfile.TemporaryDirectory() as tmp:
        norm = os.path.join(tmp, "norm.wav")
        r = run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1", "-ar", "44100", norm])
        if r.returncode:
            sys.exit("Non riesco a leggere il file: " + r.stderr[-300:])
        db = livelli(norm)
        tot = len(db) * FINESTRA
        scelta = None
        for fr in FRAZIONI:
            f = frasi(db, fr, pausa)
            print(f"soglia {fr}: {len(f)} frasi trovate (attese {len(nomi)})")
            if len(f) == len(nomi):
                scelta = f
                break
        if scelta is None:
            sys.exit("Il numero di frasi non torna con nessuna soglia: controllare le pause o le frasi ripetute.")
        # volume uniforme: un solo guadagno per tutto il file, così le frasi restano coerenti tra loro
        attivi = np.concatenate([db[int(a / FINESTRA): int(b / FINESTRA)] for a, b in scelta])
        guadagno = max(-20.0, min(24.0, OBIETTIVO_DB - float(np.percentile(attivi, 75))))
        print(f"guadagno applicato: {guadagno:+.1f} dB")
        os.makedirs(out, exist_ok=True)
        for (a, b), nome in zip(scelta, nomi):
            a0, b0 = max(0, a - MARGINE), min(tot, b + MARGINE)
            dest = os.path.join(out, nome + ".mp3")
            r = run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a0:.3f}", "-to", f"{b0:.3f}", "-i", norm,
                     "-ac", "1", "-ar", "44100", "-af", f"volume={guadagno}dB,alimiter=limit=0.89",
                     "-c:a", "libmp3lame", "-b:a", "96k", dest])
            print(f"{nome}.mp3  {b0 - a0:5.1f} s  {os.path.getsize(dest) // 1024} kB")


if __name__ == "__main__":
    main()

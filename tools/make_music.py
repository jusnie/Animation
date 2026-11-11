#!/usr/bin/env python3
"""
Synthesises the background score for MIKAY - DAY 1.

Deliberately sparse and dark: soft pads, a heartbeat pulse and a low pedal tone.
It is rendered dry here and mixed far below the narration by build_audio.py, which
also ducks it under every spoken line.

Palette
  tension  D minor drone + slow pulse        (hook, setup)
  cozy     C major 6/9 pad + gentle plucks   (false safe)
  dread    D minor + Eb cluster, no rhythm   (wrongness)
  rise     ostinato pedal, filter opening    (turn)
  resolve  open fifth, hollow and bright     (button)

Run:  .venv/bin/python tools/make_music.py   ->  audio/music/{cue}.wav
"""
import os

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 48000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audio", "music")

NOTES = {
    "C1": 32.70, "D1": 36.71, "Eb1": 38.89, "F1": 43.65, "G1": 49.00, "A1": 55.00,
    "C2": 65.41, "D2": 73.42, "Eb2": 77.78, "F2": 87.31, "G2": 98.00, "A2": 110.00,
    "Bb2": 116.54, "C3": 130.81, "D3": 146.83, "Eb3": 155.56, "F3": 174.61,
    "G3": 196.00, "Ab3": 207.65, "E3": 164.81, "B2": 123.47, "A3": 220.00, "B3": 246.94, "C4": 261.63,
    "D4": 293.66, "Eb4": 311.13, "E4": 329.63, "G4": 392.00, "F4": 349.23, "A4": 440.00, "D5": 587.33,
    "A5": 880.00,
}


def tt(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


def lp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def hp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff / (SR / 2), 0.99), "high")
    return lfilter(b, a, x)


def note_osc(freq, dur, harmonics=(1.0, 0.30, 0.14, 0.06), detune=0.0, phase=0.0):
    t = tt(dur)
    x = np.zeros_like(t)
    for i, a in enumerate(harmonics, start=1):
        x += a * np.sin(2 * np.pi * freq * i * (1 + detune * (i - 1)) * t + phase * i)
    return x


def pad(freqs, dur, attack=0.9, release=1.2, cutoff=900, width=0.6, trem=0.0):
    """Soft sustained chord. Returns stereo (2, n)."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    env = np.clip(np.minimum(1, t / attack) * np.minimum(1, (dur - t) / release), 0, 1) ** 1.3
    if trem:
        env = env * (1 - trem * 0.5 * (1 + np.sin(2 * np.pi * 0.27 * t)))
    L, R = np.zeros(n), np.zeros(n)
    for k, f in enumerate(freqs):
        a = note_osc(f, dur, detune=0.0012, phase=k * 0.7)
        b = note_osc(f, dur, detune=0.0016, phase=k * 1.9)
        d = np.sin(2 * np.pi * (0.07 + 0.02 * k) * t) * width
        L += a * (1 - d) + b * d * 0.5
        R += b * (1 - d) + a * d * 0.5
    L, R = lp(L, cutoff), lp(R, cutoff - 60)
    g = env / (len(freqs) * 1.2)
    return np.vstack([L * g, R * g])


def pluck(freq, dur=1.2, decay=3.2, bright=0.5, pan=0.0):
    t = tt(dur)
    x = (np.sin(2 * np.pi * freq * t) * 1.0
         + np.sin(2 * np.pi * freq * 2 * t) * 0.28 * bright
         + np.sin(2 * np.pi * freq * 3 * t) * 0.10 * bright)
    x *= np.exp(-t * decay) * np.minimum(1, t / 0.006)
    x = lp(x, 3500)
    a = (pan + 1) / 2
    return np.vstack([x * np.sqrt(1 - a), x * np.sqrt(a)])


def heartbeat_pulse(dur, bpm=52, gain=1.0):
    n = int(SR * dur)
    out = np.zeros((2, n))
    period = 60 / bpm
    t0 = 0.0
    while t0 < dur - 0.4:
        for off, amp in ((0.0, 1.0), (0.20, 0.72)):
            t = tt(0.42)
            th = np.sin(2 * np.pi * (52 * np.exp(-t * 9) + 32) * t) * np.exp(-t * 14)
            s = int(SR * (t0 + off))
            e = min(n, s + len(th))
            if s < n:
                out[0, s:e] += th[:e - s] * amp * gain
                out[1, s:e] += th[:e - s] * amp * gain
        t0 += period
    return out


def place(buf, x, at, gain=1.0):
    s = int(SR * at)
    e = min(buf.shape[1], s + x.shape[1])
    if s >= buf.shape[1] or e <= s:
        return
    buf[:, s:e] += x[:, :e - s] * gain


def rise_pad(freqs, dur, cutoff_from=350, cutoff_to=2400, attack=0.4, release=0.6):
    """Chord whose filter opens across its length - used to build the turn."""
    steps = 24
    n = int(SR * dur)
    out = np.zeros((2, n))
    for i in range(steps):
        s = int(n * i / steps)
        e = int(n * (i + 1) / steps) + int(SR * 0.12)
        seg = pad(freqs, (e - s) / SR, attack=0.08, release=0.12,
                  cutoff=cutoff_from + (cutoff_to - cutoff_from) * (i / steps))
        place(out, seg, s / SR, 1.0)
    t = np.arange(n) / SR
    env = np.clip(np.minimum(1, t / attack) * np.minimum(1, (dur - t) / release), 0, 1) ** 1.2
    return out * env


def shimmer(dur, freq=880.0, gain=0.25):
    t = tt(dur)
    x = np.sin(2 * np.pi * freq * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t))
    x += np.sin(2 * np.pi * freq * 1.5 * t) * 0.25
    x *= np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return np.vstack([x * gain, np.roll(x, 240) * gain])


def build_cues():
    cues = {}

    # ---- tension: the night before                     (hook + setup ~ 10.4s)
    b = np.zeros((2, int(SR * 10.6)))
    place(b, pad([NOTES["D2"], NOTES["D3"], NOTES["F3"]], 10.6, attack=0.8,
                 release=1.8, cutoff=520, trem=0.25), 0.0, 0.9)
    place(b, pad([NOTES["D1"]], 10.6, attack=1.2, release=2.0, cutoff=200), 0.0, 0.7)
    place(b, heartbeat_pulse(10.6, bpm=50, gain=0.35), 0.0, 1.0)
    place(b, shimmer(6.0, NOTES["D5"], 0.06), 3.2, 1.0)
    cues["tension"] = b

    # ---- cozy: cereal on the sofa                       (false safe ~ 10.3s)
    b = np.zeros((2, int(SR * 10.4)))
    place(b, pad([NOTES["C3"], NOTES["E3"], NOTES["G3"], NOTES["A3"]], 10.4, attack=1.2,
                 release=1.6, cutoff=1500, trem=0.15), 0.0, 0.85)
    place(b, pad([NOTES["C2"], NOTES["G2"]], 10.4, attack=1.8, cutoff=300), 0.0, 0.6)
    # lazy plucked figure, deliberately out of time with the narration
    for i, nme in enumerate(["C4", "E4", "G3", "A3", "G3", "E4", "C4", "A3"]):
        place(b, pluck(NOTES[nme], 1.6, 2.4, 0.35, pan=-0.35 + 0.1 * (i % 3)),
              i * 1.28 + 0.25, 0.30)
    cues["cozy"] = b

    # ---- the mistake: warmth drains out                (~2.6s)
    b = np.zeros((2, int(SR * 2.7)))
    place(b, pad([NOTES["C3"], NOTES["Eb3"], NOTES["Ab3"]], 2.7, attack=0.35,
                 release=0.8, cutoff=700), 0.0, 0.85)
    place(b, pad([NOTES["C1"]], 2.7, attack=0.4, cutoff=180), 0.0, 0.6)
    cues["mistake"] = b

    # ---- dread: they were not trying to get in          (~5.4s)
    b = np.zeros((2, int(SR * 5.5)))
    place(b, pad([NOTES["D3"], NOTES["F3"], NOTES["Eb3"]], 5.5, attack=1.4,
                 release=1.6, cutoff=650, trem=0.3), 0.0, 0.85)
    place(b, pad([NOTES["D1"], NOTES["A1"]], 5.5, attack=1.8, cutoff=190), 0.0, 0.6)
    place(b, heartbeat_pulse(5.5, bpm=44, gain=0.28), 0.0, 1.0)
    cues["dread"] = b

    # ---- the turn: filter opens as she looks up         (~7.4s)
    b = np.zeros((2, int(SR * 7.6)))
    place(b, rise_pad([NOTES["D3"], NOTES["F3"], NOTES["A3"]], 7.6,
                      cutoff_from=320, cutoff_to=2600), 0.0, 0.8)
    place(b, pad([NOTES["D1"]], 7.6, attack=0.6, cutoff=200), 0.0, 0.55)
    # eighth-note pedal, quiet, tempo drifts slightly faster
    step, t_acc = 0.42, 0.4
    while t_acc < 6.4:
        nme = "D2" if step % 2 == 0 else "A2"
        place(b, pluck(NOTES[nme], 0.5, 9.0, 0.15, pan=0.0), t_acc, 0.22)
        t_acc += step
        step = 1 if step == 0 else 0
    cues["turn"] = b

    # ---- the door: hollow resolution                    (~5.4s)
    b = np.zeros((2, int(SR * 5.6)))
    place(b, pad([NOTES["D3"], NOTES["A3"], NOTES["D4"]], 5.6, attack=0.8,
                 release=1.8, cutoff=2000), 0.0, 0.8)
    place(b, pad([NOTES["D2"]], 5.6, attack=1.2, cutoff=260), 0.0, 0.5)
    place(b, shimmer(4.4, NOTES["A5"], 0.10), 0.6, 1.0)
    place(b, pluck(NOTES["D5"], 3.0, 1.1, 0.5), 0.35, 0.22)
    cues["resolve"] = b

    # ---- end card: one low bloom                        (~3.0s)
    b = np.zeros((2, int(SR * 3.1)))
    place(b, pad([NOTES["D2"], NOTES["D3"]], 3.1, attack=0.5, release=2.4,
                 cutoff=420), 0.0, 0.7)
    cues["end"] = b
    return cues


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, buf in build_cues().items():
        peak = np.max(np.abs(buf)) + 1e-9
        stereo = (buf / peak * 0.85).T          # scipy wants (frames, channels)
        wavfile.write(os.path.join(OUT, f"{name}.wav"), SR,
                      (stereo * 32767).astype(np.int16))
        print("music:", name, f"{buf.shape[1]/SR:.1f}s")

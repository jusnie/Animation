#!/usr/bin/env python3
"""
Procedurally synthesises every sound effect used in MIKAY - DAY 1.

Nothing is sampled: each cue is built from oscillators and filtered noise so the repo
stays small and every effect is licence-free. Output: audio/sfx/*.wav (48 kHz mono).

Run:  .venv/bin/python tools/make_sfx.py
"""
import os

import numpy as np
from scipy.signal import butter, fftconvolve, lfilter
from scipy.io import wavfile

SR = 48000
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "audio", "sfx")
rng = np.random.default_rng(7)


# ----------------------------------------------------------------------------- helpers
def tt(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


def lp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def hp(x, cutoff, order=2):
    b, a = butter(order, min(cutoff / (SR / 2), 0.99), "high")
    return lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, x)


def noise(dur):
    return rng.standard_normal(int(SR * dur))


def env_ad(n, attack, decay, shape=3.0):
    a = int(SR * attack)
    d = max(1, n - a)
    e = np.concatenate([np.linspace(0, 1, max(1, a)), np.linspace(1, 0, d) ** shape])
    return e[:n]


def reverb(x, decay=0.9, mix=0.3, tone=4000):
    n = int(SR * decay)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lp(ir, tone)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = fftconvolve(x, ir)[:len(x)]
    return (1 - mix) * x + mix * wet


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x * (peak / m)


def save(name, x, peak=0.9):
    os.makedirs(OUT, exist_ok=True)
    x = norm(np.asarray(x, dtype=np.float64), peak)
    wavfile.write(os.path.join(OUT, f"{name}.wav"), SR, (x * 32767).astype(np.int16))


# --------------------------------------------------------------------------- the cues
def bang(level=1.0):
    """Fist on a wooden door: hard transient + low body + wood rattle."""
    t = tt(0.55)
    thump = np.sin(2 * np.pi * (58 * np.exp(-t * 12) + 34) * t) * np.exp(-t * 13)
    knock = lp(noise(0.55), 1800) * np.exp(-t * 45) * 0.8
    rattle = bp(noise(0.55), 250, 900) * np.exp(-t * 8) * 0.18
    x = thump * 0.9 + knock + rattle
    return reverb(x, 0.35, 0.18, 2500) * level


def bang_series(n=3, gap=0.34):
    out = np.zeros(int(SR * (0.55 + gap * (n - 1))))
    for i in range(n):
        b = bang(0.85 - i * 0.12)
        s = int(SR * gap * i)
        out[s:s + len(b)] += b
    return out


def hammer():
    """Steel head on a nail: click, metallic ring, then the wood taking it."""
    t = tt(0.5)
    click = hp(noise(0.5), 3000) * np.exp(-t * 220) * 1.0
    ring = (np.sin(2 * np.pi * 3150 * t) * 0.5 + np.sin(2 * np.pi * 4680 * t) * 0.3
            ) * np.exp(-t * 55)
    head = np.sin(2 * np.pi * (150 * np.exp(-t * 20) + 90) * t) * np.exp(-t * 26) * 0.7
    wood = bp(noise(0.5), 400, 1600) * np.exp(-t * 30) * 0.35
    return reverb(click + ring * 0.5 + head + wood, 0.5, 0.22, 5000)


def glass_ting(freqs=(2310, 3120, 4270), dur=0.45, gain=1.0):
    t = tt(dur)
    x = np.zeros_like(t)
    for i, f in enumerate(freqs):
        x += np.sin(2 * np.pi * f * t) * np.exp(-t * (11 + i * 5)) / (i + 1.6)
    x += hp(noise(dur), 5000) * np.exp(-t * 160) * 0.5
    return reverb(x * gain, 0.6, 0.3, 7000)


def spoon_clink():
    t = tt(0.35)
    x = (np.sin(2 * np.pi * 2650 * t) * np.exp(-t * 26)
         + np.sin(2 * np.pi * 3900 * t) * np.exp(-t * 34) * 0.6)
    x += hp(noise(0.35), 6000) * np.exp(-t * 200) * 0.5
    return reverb(x, 0.4, 0.2, 8000)


def zombie_moan(dur=1.9, f0=96.0, seed=None):
    """A slack, vocal-ish groan: jittered harmonic stack through a formant filter."""
    if seed is not None:
        np.random.seed(seed)
    t = tt(dur)
    vib = 1 + 0.03 * np.sin(2 * np.pi * 5.1 * t + 0.7) + 0.02 * np.sin(2 * np.pi * 1.3 * t)
    f = f0 * vib * (1 - 0.12 * t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    voice = (np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.28 * np.sin(3 * phase)
             + 0.15 * np.sin(4 * phase) + 0.09 * np.sin(5 * phase))
    voice = bp(voice, 180, 1100) * 0.8 + bp(voice, 700, 2400) * 0.25
    breath = bp(noise(dur), 300, 2600) * 0.22
    e = np.minimum(1, t / 0.18) * np.minimum(1, (dur - t) / 0.35)
    e *= 0.75 + 0.25 * np.sin(2 * np.pi * 2.7 * t)
    return reverb((voice + breath) * e, 1.1, 0.35, 3000)


def horde_murmur(dur=6.0):
    """Distant crowd of moans, used as a bed under the exterior shots."""
    out = np.zeros(int(SR * dur))
    for i in range(9):
        d = 1.6 + rng.random() * 1.5
        m = zombie_moan(dur=d, f0=78 + rng.random() * 55, seed=int(rng.integers(1 << 30)))
        s = int(SR * rng.random() * max(0.1, dur - d))
        out[s:s + len(m)] += m * (0.3 + rng.random() * 0.45)
    out = lp(out, 1600)
    return reverb(out, 1.6, 0.45, 2200)


def breath(dur=0.65):
    t = tt(dur)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return bp(noise(dur), 420, 2600) * e


def scratch(dur=1.3):
    """Fingernails dragging on a door."""
    t = tt(dur)
    mod = 0.45 + 0.55 * np.abs(np.sin(2 * np.pi * 6.5 * t + rng.random()))
    x = bp(noise(dur), 900, 3400) * mod * np.minimum(1, (dur - t) / 0.3)
    return reverb(x * 0.8, 0.5, 0.2, 6000)


def heartbeat(times=2):
    out = np.zeros(int(SR * 1.7))
    for i in range(times):
        t = tt(0.34)
        thud = np.sin(2 * np.pi * (48 * np.exp(-t * 9) + 30) * t) * np.exp(-t * 15)
        thud += lp(noise(0.34), 300) * np.exp(-t * 40) * 0.4
        s = int(SR * (0.0 if i == 0 else 0.33))
        out[s:s + len(thud)] += thud * (1.0 if i == 0 else 0.72)
    return out


def creak(dur=1.4):
    """Dry hinge: pitch-drifting resonant squeal plus the board settling."""
    t = tt(dur)
    drift = 1 + 0.35 * np.sin(2 * np.pi * 0.8 * t) + 0.12 * np.sin(2 * np.pi * 3.3 * t)
    f = 320 * drift * (1 + 0.9 * t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    squeal = np.sign(np.sin(phase)) * 0.25 + np.sin(phase * 2) * 0.2
    squeal = bp(squeal, 250, 2600) * (0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 11 * t)))
    settle = lp(noise(dur), 700) * np.exp(-t * 6) * 0.5
    e = np.minimum(1, t / 0.12) * np.minimum(1, (dur - t) / 0.25)
    return reverb((squeal + settle) * e, 0.9, 0.3, 4000)


def whoosh(dur=0.9):
    t = tt(dur)
    sweep = 300 + 2200 * np.sin(np.pi * t / dur) ** 2
    bands = np.zeros_like(t)
    step = 512
    for i in range(0, len(t), step):
        n = noise(step / SR)
        bands[i:i + step] += bp(n, sweep[i] * 0.6, sweep[i] * 1.5)[:len(t) - i]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.4
    return reverb(bands * e, 0.7, 0.25, 6000)


def riser(dur=2.2):
    t = tt(dur)
    f = 180 * np.exp(np.log(6.0) * t / dur)
    phase = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(phase) * 0.5 + np.sin(2 * phase) * 0.2
    air = hp(noise(dur), 1200) * 0.35
    e = (t / dur) ** 2.2
    return reverb((tone + air) * e, 1.0, 0.3, 5000)


def boom(dur=2.8):
    t = tt(dur)
    sub = np.sin(2 * np.pi * (42 * np.exp(-t * 2.2) + 22) * t) * np.exp(-t * 1.6)
    hit = lp(noise(dur), 900) * np.exp(-t * 5) * 0.5
    tail = reverb(lp(noise(dur), 500) * np.exp(-t * 3) * 0.25, 2.2, 0.6, 1200)
    return norm(sub * 1.0 + hit + tail) * 0.95


def door_open():
    """Latch, hinge, and the air moving past the frame."""
    latch = glass_ting((1450, 2100, 3050), 0.25, 0.7)
    out = np.zeros(int(SR * 1.8))
    out[:len(latch)] += latch * 0.6
    cr = creak(1.2) * 0.9
    out[int(SR * 0.18):int(SR * 0.18) + len(cr)] += cr
    wh = whoosh(0.7) * 0.5
    out[int(SR * 0.9):int(SR * 0.9) + len(wh)] += wh
    return out


def tv_static(dur=2.4):
    """A old television idling: hiss, mains hum and occasional crackle."""
    t = tt(dur)
    hiss = bp(noise(dur), 900, 7000) * 0.35
    hum = np.sin(2 * np.pi * 60 * t) * 0.05 + np.sin(2 * np.pi * 120 * t) * 0.03
    crackle = np.zeros_like(t)
    for _ in range(26):
        s = int(rng.random() * (len(t) - 400))
        burst = hp(noise(0.008), 2000) * 0.6
        crackle[s:s + len(burst)] += burst[:len(crackle) - s]
    return lp(hiss + hum + crackle, 8000) * 0.8


def clink_bowl():
    return glass_ting((1750, 2600, 3600), 0.5, 0.55)


def wind(dur=8.0):
    """Cold night air: slow band-swept noise, almost subliminal."""
    t = tt(dur)
    n = noise(dur)
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + 0.4)
    body = lp(n, 700) * 0.7 + bp(n, 300, 1500) * 0.3
    return reverb(body * (0.45 + 0.55 * mod), 2.0, 0.4, 1800) * 0.5


def room_tone(dur=6.0):
    """Interior quiet: low rumble plus a faint fridge hum."""
    t = tt(dur)
    rumble = lp(noise(dur), 160) * 0.6
    hum = np.sin(2 * np.pi * 50 * t) * 0.012 + np.sin(2 * np.pi * 100 * t) * 0.006
    return rumble + hum


# --------------------------------------------------------------- calm / everyday cue
def alarm_ring(dur=2.6):
    """Old twin-bell alarm clock: hammered bell at ~2 beats a second."""
    t = tt(dur)
    out = np.zeros_like(t)
    beat = 0.0
    while beat < dur - 0.2:
        n = int(SR * 0.09)
        tb = np.linspace(0, 0.09, n, endpoint=False)
        strike = (np.sin(2 * np.pi * 2100 * tb) * 0.5
                  + np.sin(2 * np.pi * 3180 * tb) * 0.3
                  + np.sin(2 * np.pi * 4700 * tb) * 0.15) * np.exp(-tb * 45)
        strike += hp(noise(0.09), 4000) * np.exp(-tb * 120) * 0.4
        s0 = int(SR * beat)
        out[s0:s0 + n] += strike[:len(out) - s0]
        beat += 0.055 if (beat % 0.11) < 0.05 else 0.055
    out *= 0.55
    return reverb(out, 0.5, 0.25, 6000)


def birds(dur=5.0, density=7):
    """Morning birdsong: short FM chirps scattered across the bed."""
    out = np.zeros(int(SR * dur))
    for _ in range(density):
        start = rng.random() * (dur - 0.5)
        for k in range(int(rng.integers(2, 5))):
            d = 0.05 + rng.random() * 0.05
            t = tt(d)
            f = 2200 + rng.random() * 1800 + 600 * np.sin(np.pi * t / d)
            phase = 2 * np.pi * np.cumsum(f) / SR
            chirp = np.sin(phase) * np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
            s0 = int(SR * (start + k * 0.09))
            e = min(len(out), s0 + len(chirp))
            if s0 < len(out):
                out[s0:e] += chirp[:e - s0] * (0.35 + rng.random() * 0.3)
    return reverb(lp(out, 7000), 1.2, 0.35, 6000) * 0.8


def toothbrush(dur=2.4):
    """Bristles on teeth: fast, dry, granular scrubbing."""
    t = tt(dur)
    mod = 0.25 + 0.75 * np.abs(np.sin(2 * np.pi * 4.2 * t)) ** 0.6
    x = bp(noise(dur), 1600, 6000) * mod
    x *= np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.2)
    return x * 0.9


def tap_water(dur=1.8):
    t = tt(dur)
    body = bp(noise(dur), 500, 4200) * 0.45
    splash = bp(noise(dur), 1800, 7000) * (0.2 + 0.2 * np.sin(2 * np.pi * 7 * t))
    e = np.minimum(1, t / 0.12) * np.minimum(1, (dur - t) / 0.3)
    return (body + splash) * e * 0.8


def footsteps(dur=3.2, pace=0.46):
    """Soft sneakers on concrete, alternating pan."""
    out = np.zeros((int(SR * dur),))
    t_acc = 0.05
    i = 0
    while t_acc < dur - 0.3:
        t = tt(0.16)
        step = lp(noise(0.16), 900) * np.exp(-t * 34) * 0.8
        step += np.sin(2 * np.pi * (95 * np.exp(-t * 22) + 55) * t) * np.exp(-t * 30) * 0.5
        s0 = int(SR * t_acc)
        e = min(len(out), s0 + len(step))
        out[s0:e] += step[:e - s0] * (0.8 if i % 2 == 0 else 0.65)
        t_acc += pace * (0.95 + 0.1 * rng.random())
        i += 1
    return out


def sprinkler(dur=4.0):
    """A lawn sprinkler's slow chuff-chuff hiss."""
    t = tt(dur)
    mod = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.5 * t)) ** 2
    x = bp(noise(dur), 900, 6500) * mod
    return x * 0.75


def dog_bark(dur=1.1):
    out = np.zeros(int(SR * dur))
    for i, off in enumerate((0.0, 0.34)):
        d = 0.16
        t = tt(d)
        f = 300 * np.exp(-t * 6) + 150
        phase = 2 * np.pi * np.cumsum(f) / SR
        bark = (np.sin(phase) + 0.6 * np.sin(2 * phase)) * np.exp(-t * 16)
        bark = bp(bark, 180, 2600) + bp(noise(d), 400, 3000) * np.exp(-t * 20) * 0.5
        s0 = int(SR * off)
        out[s0:s0 + len(bark)] += bark[:len(out) - s0] * (0.9 - i * 0.15)
    return reverb(out, 1.4, 0.4, 3500) * 0.55


def crickets(dur=6.0):
    """Night crickets: a pulsed 4.5 kHz tone with a slow chorus drift."""
    t = tt(dur)
    pulse = (0.5 + 0.5 * np.sin(2 * np.pi * 21 * t)) ** 6
    tone = np.sin(2 * np.pi * 4500 * t) * 0.5 + np.sin(2 * np.pi * 4300 * t) * 0.35
    swell = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t))
    x = tone * pulse * swell
    return reverb(x, 1.8, 0.4, 8000) * 0.30


def phone_buzz(dur=0.9):
    t = tt(dur)
    mod = (0.5 + 0.5 * np.sin(2 * np.pi * 28 * t))
    x = np.sin(2 * np.pi * 165 * t) * mod + np.sin(2 * np.pi * 330 * t) * 0.2 * mod
    e = np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.1)
    return lp(x * e, 1200) * 0.7


def cloth_rustle(dur=1.1):
    t = tt(dur)
    mod = 0.2 + 0.8 * np.abs(np.sin(2 * np.pi * 3.1 * t + 0.7)) ** 2
    x = bp(noise(dur), 700, 3500) * mod
    x *= np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.35)
    return x * 0.7


def tv_news(dur=7.0):
    """Muffled broadcast: a voice-ish murmur under a television's speaker."""
    out = np.zeros(int(SR * dur))
    t_acc = 0.0
    while t_acc < dur - 0.6:
        d = 0.24 + rng.random() * 0.3
        t = tt(d)
        f0 = 118 + rng.random() * 70
        f = f0 * (1 + 0.06 * np.sin(2 * np.pi * 3.3 * t))
        phase = 2 * np.pi * np.cumsum(f) / SR
        v = (np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.3 * np.sin(3 * phase))
        v = bp(v, 250, 1800)
        e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5
        s0 = int(SR * t_acc)
        e_i = min(len(out), s0 + len(v))
        out[s0:e_i] += (v * e)[:e_i - s0] * (0.5 + rng.random() * 0.4)
        t_acc += d + 0.03 + rng.random() * 0.09
    hiss = bp(noise(dur), 2000, 7000) * 0.05
    return lp(out + hiss, 4200) * 0.9


CUES = {
    "bang": lambda: bang(),
    "bang_series": lambda: bang_series(3),
    "bang_soft": lambda: bang(0.45),
    "hammer": hammer,
    "glass_ting": glass_ting,
    "spoon": spoon_clink,
    "bowl": clink_bowl,
    "moan1": lambda: zombie_moan(1.9, 96, seed=3),
    "moan2": lambda: zombie_moan(2.2, 74, seed=11),
    "moan3": lambda: zombie_moan(1.6, 118, seed=23),
    "horde": lambda: horde_murmur(7.0),
    "breath": breath,
    "scratch": scratch,
    "heartbeat": heartbeat,
    "creak": creak,
    "whoosh": whoosh,
    "riser": riser,
    "boom": boom,
    "door_open": door_open,
    "tv": tv_static,
    "wind": wind,
    "room": room_tone,
    "alarm": alarm_ring,
    "birds": birds,
    "brush": toothbrush,
    "tap": tap_water,
    "steps": footsteps,
    "sprinkler": sprinkler,
    "dog": dog_bark,
    "crickets": crickets,
    "phone": phone_buzz,
    "cloth": cloth_rustle,
    "tvnews": tv_news,
}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in CUES.items():
        save(name, fn())
        print("sfx:", name)
    print(f"{len(CUES)} cues -> {OUT}")

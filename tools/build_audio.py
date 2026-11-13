#!/usr/bin/env python3
"""
Mixes narration + sound effects into the master track for one film.

No music: the score was removed on request. Effects are placed against the exact words
they belong to and are pulled down slightly while the narrator is speaking, so the
voice always sits on top.

Run:  .venv/bin/python tools/build_audio.py [day0|day1]   (default: day0)
Out:  render/mikay-day0_mix.wav  +  render/audio-plan-day0.json
"""
import json
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile

import script_data as S

SR = 48000
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SFX = os.path.join(S.ROOT, "audio", "sfx")

VO_GAIN = 1.0
SFX_GAIN = 0.60
DUCK_TO = 0.50          # effects are halved while she speaks
DUCK_RELEASE = 0.25


def load(path):
    _, x = wavfile.read(path)
    x = x.astype(np.float64) / 32768.0
    return np.vstack([x, x]) if x.ndim == 1 else x.T


def load_mp3(path):
    tmp = os.path.join(S.OUT, "_vo_tmp.wav")
    os.makedirs(S.OUT, exist_ok=True)
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", path,
                    "-ar", str(SR), "-ac", "2", tmp], check=True)
    return load(tmp)


def add(buf, x, at, gain=1.0):
    s = int(SR * at)
    if s >= buf.shape[1]:
        return
    e = min(buf.shape[1], s + x.shape[1])
    if e > s:
        buf[:, s:e] += x[:, :e - s] * gain


def smooth_env(x, attack=0.02, release=DUCK_RELEASE):
    a, r = np.exp(-1 / (attack * SR)), np.exp(-1 / (release * SR))
    env, prev = np.zeros_like(x), 0.0
    for i, v in enumerate(x):
        c = a if v > prev else r
        prev = c * prev + (1 - c) * v
        env[i] = prev
    return env


# --------------------------------------------------------------------------------------
# Cue sheets: (effect, offset from the segment start OR absolute, gain, note)
#   ("anchor", id, offset)  -> absolute time relative to that narration line
# --------------------------------------------------------------------------------------
CUE_SHEETS = {
    "day0": [
        # ---- waking up
        ("alarm", ("d1", 0.10), 0.55, "the alarm clock is ringing"),
        ("birds", ("d1", 0.30), 0.50, "birdsong through the window"),
        ("cloth", ("d2", 0.35), 0.45, "snooze: she rolls over"),
        ("alarm", ("d2", 0.85), 0.30, "the ringing continues, muffled"),
        ("cloth", ("d2", 1.85), 0.35, "blanket thrown back"),
        # ---- bathroom
        ("tap", ("d3", 0.10), 0.55, "the tap running"),
        ("brush", ("d3", 0.55), 0.45, "toothbrush"),
        ("tap", ("d3", 1.85), 0.35, "tap off, water draining"),
        # ---- the street
        ("steps", ("d4", 0.20), 0.55, "sneakers on the sidewalk"),
        ("birds", ("d4", 0.50), 0.45, "morning birds"),
        ("sprinkler", ("d4", 2.30), 0.40, "a lawn sprinkler"),
        ("dog", ("d4", 3.40), 0.40, "a dog behind a fence"),
        # ---- afternoon, the television
        ("tvnews", ("d5", 0.25), 0.55, "the television: news broadcast"),
        ("spoon", ("d5", 1.55), 0.40, "cereal"),
        ("bowl", ("d5", 2.80), 0.30, "bowl set down"),
        ("tvnews", ("d5", 4.10), 0.30, "she changes the channel"),
        ("phone", ("d5", -10.0), 0.55, "her phone buzzes, ignored"),
        ("phone", ("d5", -6.0), 0.45, "a second buzz, ignored"),
        # ---- the porch
        ("birds", ("d6", 0.20), 0.40, "evening birds"),
        ("cloth", ("d6", 2.30), 0.25, "she stands, stretches"),
        ("steps", ("d6", 3.10), 0.40, "boots on the porch boards"),
        # ---- night
        ("crickets", ("d7", 0.20), 0.55, "crickets"),
        ("room", ("d7", 0.20), 0.45, "the house settling"),
        ("phone", ("d7", 3.10), 0.35, "a notification on the nightstand"),
        ("boom", ("d7", 0.10), 0.30, "a submarine swell under the last line"),
    ],
    "day1": [
        ("bang", 0.04, 0.95, "palm slams the door on the hook"),
        ("wind", 0.60, 0.35, "cold night air bed"),
        ("bang_soft", 1.85, 0.45, "second, weaker hit"),
        ("breath", 2.35, 0.55, "her breath catches"),
        ("hammer", ("n2", 0.25), 1.00, "first nail"),
        ("hammer", ("n2", 0.78), 0.90, "second nail"),
        ("hammer", ("n2", 1.31), 1.00, "third nail"),
        ("hammer", ("n2", 1.72), 0.75, "fourth nail"),
        ("creak", ("n2", 2.55), 0.40, "board flexing"),
        ("horde", ("n2", 3.30), 0.55, "she looks through the window"),
        ("moan1", ("n2", 5.10), 0.50, "a zombie answers"),
        ("glass_ting", ("n2", 5.35), 0.35, "ring of the pane"),
        ("spoon", ("n3", 0.30), 0.45, "spoon on the bowl"),
        ("bowl", ("n3", 0.85), 0.35, "bowl set down"),
        ("tv", ("n3", 1.30), 0.30, "television idling in the corner"),
        ("spoon", ("n3", 3.10), 0.40, "another spoonful"),
        ("bang_soft", ("n3", 4.60), 0.32, "distant knock, ignored"),
        ("scratch", ("n3", 6.05), 0.25, "fingernails on the far door"),
        ("bowl", ("n3", 7.40), 0.28, "bowl down"),
        ("heartbeat", ("n3", 8.75), 0.55, "she realises"),
        ("creak", ("n3", 9.90), 0.30, "house settling"),
        ("moan2", ("n4", 0.55), 0.45, "close, quiet moan"),
        ("heartbeat", ("n4", 1.60), 0.50, "her pulse"),
        ("scratch", ("n4", 3.05), 0.30, "hand dragging on glass"),
        ("moan3", ("n4", 3.90), 0.38, "another one joins"),
        ("glass_ting", ("n4", 4.62), 0.22, "fingertip tap"),
        ("scratch", ("n5", 0.28), 0.42, "hand pressed on the glass"),
        ("glass_ting", ("n5", 0.95), 0.30, "tap"),
        ("riser", ("n5", 1.85), 0.55, "it points up"),
        ("creak", ("n5", 3.05), 0.65, "the attic hatch"),
        ("whoosh", ("n5", 3.55), 0.35, "dust falling"),
        ("heartbeat", ("n5", 5.10), 0.60, "she understands"),
        ("breath", ("n5", 6.10), 0.50, "sharp intake"),
        ("door_open", ("n6", 0.10), 0.75, "bolt, hinge, air"),
        ("wind", ("n6", 0.70), 0.55, "night air through the open door"),
        ("boom", ("n6", 1.55), 0.65, "the horde shifts to let her through"),
        ("horde", ("n6", 1.90), 0.45, "the horde, quiet"),
    ],
}


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else S.DEFAULT_FILM
    spec = S.film(key)
    os.makedirs(S.OUT, exist_ok=True)
    timeline, total = S.build_timeline(spec, FFMPEG)
    n = int(SR * total)
    vo = np.zeros((2, n))
    sfx = np.zeros((2, n))
    plan = {"film": key, "total": round(total, 3), "voice": [], "sfx": []}

    for seg in timeline:
        add(vo, load_mp3(os.path.join(S.AUDIO, seg["audio"])), seg["start"], VO_GAIN)
        plan["voice"].append(dict(id=seg["id"], start=round(seg["start"], 3),
                                  end=round(seg["start"] + seg["audio_dur"], 3)))

    starts = {s["id"]: s for s in timeline}
    for cue in CUE_SHEETS.get(key, []):
        name, where, gain, note = cue
        if isinstance(where, tuple):
            anchor, off = where
            at = starts[anchor]["start"] + off
        else:
            at = where
        x = load(os.path.join(SFX, f"{name}.wav"))
        add(sfx, x, at, gain * SFX_GAIN)
        plan["sfx"].append(dict(cue=name, at=round(at, 3), gain=round(gain, 2), note=note))

    # duck the effects under the voice
    env = smooth_env(np.max(np.abs(vo), axis=0))
    key_env = np.clip(env / (np.percentile(env[env > 0.01], 90) + 1e-9), 0, 1)
    sfx *= 1.0 - (1.0 - DUCK_TO) * key_env
    plan["ducking"] = dict(ducked_to_db=round(20 * np.log10(DUCK_TO), 1),
                           release_ms=int(DUCK_RELEASE * 1000))

    mix = vo * VO_GAIN + sfx
    peak = np.max(np.abs(mix)) + 1e-9
    mix = np.tanh(mix / peak * 1.05 * 1.15) / np.tanh(1.15)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89

    if "--stems" in sys.argv:
        qa = os.path.join(S.OUT, "qa")
        os.makedirs(qa, exist_ok=True)
        for nm, stem in (("voice", vo), ("sfx", sfx)):
            wavfile.write(os.path.join(qa, f"{key}-{nm}.wav"), SR,
                          (stem.T * 32767).astype(np.int16))

    out = os.path.join(S.OUT, f"{spec['slug']}_mix.wav")
    wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
    with open(os.path.join(S.OUT, f"audio-plan-{key}.json"), "w") as fh:
        json.dump(plan, fh, indent=2)

    tmp = os.path.join(S.OUT, "_vo_tmp.wav")
    if os.path.exists(tmp):
        os.remove(tmp)
    print(f"mixed: {out}  {total:.2f}s  {len(plan['sfx'])} cues")


if __name__ == "__main__":
    main()

"""Shared script + timing data for every MIKAY film.

Both the audio builder and the video builder import from here, so narration, subtitles
and sound effects can never fall out of sync. The spoken string and the burned-in
subtitle string are literally the same value.

    .venv/bin/python tools/build_audio.py day0
    .venv/bin/python tools/build_video.py day0
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "render")
AUDIO = os.path.join(ROOT, "audio")
FRAMES = os.path.join(ROOT, "art", "frames")
PRE = os.path.join(ROOT, "art", "pre")
FONTS = os.path.join(ROOT, "assets", "fonts")

W, H = 1920, 1080
FPS = 24
TAIL = 0.50
FADE = 0.35
TITLE_SHOW = 0.0      # the opening title card carries the badge; no overlay on frames

# --------------------------------------------------------------------------------------
# FILM: day0 — "the day before", deliberately uneventful
# --------------------------------------------------------------------------------------
DAY0 = dict(
    slug="mikay-day0",
    title_badge="MIKAY",
    title_big="THE DAY BEFORE",
    end_card=dict(big="DAY 1.", small="THEY'RE OUTSIDE."),
    end_hold=3.0,
    lead_in=1.5,
    # (id, frame, audio, spoken text == subtitle text)
    narration=[
        dict(id="d1", frame="p1-morning.png", audio="d1.mp3",
             text="This is what a normal day looked like. I didn't know it yet."),
        dict(id="d2", frame="p1b-alarm.png", audio="d2.mp3",
             text="My alarm went off at seven. I hit snooze twice, like always."),
        dict(id="d3", frame="p2-bathroom.png", audio="d3.mp3",
             text="I brushed my teeth in the same mirror, with the same face."),
        dict(id="d4", frame="p3-street.png", audio="d4.mp3",
             text="Walked to the bus stop past the same houses. The same cat sat on "
                  "the same fence."),
        dict(id="d5", frame="p4-tv.png", audio="d5.mp3",
             text="Afternoon cartoons. Then the news said a city name I had never "
                  "heard of. I changed the channel."),
        dict(id="d6", frame="p5-porch.png", audio="d7.mp3",
             text="I sat on the porch until the streetlights came on. It was the best "
                  "day I ever had."),
        dict(id="d7", frame="p6-night.png", audio="d6.mp3",
             text="That night I left my window open. Someone was standing under the "
                  "streetlight. I figured they were waiting for a friend."),
    ],
)

# --------------------------------------------------------------------------------------
# FILM: day1 — the outbreak
# --------------------------------------------------------------------------------------
DAY1 = dict(
    slug="mikay-day1",
    title_badge="MIKAY",
    title_big="DAY 1",
    end_card=dict(big="DAY 4.", small="THEY WEREN'T TRYING TO GET IN."),
    end_hold=2.6,
    lead_in=1.5,
    narration=[
        dict(id="n1", frame="f1-hook.png", audio="n1.mp3",
             text="Day one. I did everything right."),
        dict(id="n2", frame="f2-setup.png", audio="n2.mp3",
             text="I nailed boards over the front door and told myself they would hold. "
                  "Then I looked through the window. There were so many of them."),
        dict(id="n3", frame="f3-false-safe.png", audio="n3.mp3",
             text="Day two, they were still there. Day three... they still hadn't moved. "
                  "So I got comfortable. I stopped sleeping behind the barricade. "
                  "That was my mistake."),
        dict(id="n4", frame="f4-wrongness.png", audio="n4.mp3",
             text="Because they weren't trying to get in. They were looking at me the way "
                  "you look at someone who doesn't know yet."),
        dict(id="n5", frame="f5-turn.png", audio="n5.mp3",
             text="Then one of them pressed its hand against the glass... and pointed up. "
                  "I had been sleeping under that hatch for three days."),
        dict(id="n6", frame="f6-button.png", audio="n6.mp3",
             text="So I did the only thing left. I opened the door. And they stepped aside."),
    ],
)

# --------------------------------------------------------------------------------------
# FILM: ep0 — the animated episode. ONE caption per narration file, so a caption can
# never drift inside a sentence: the picture is drawn frame-driven and every caption
# owns exactly the measured length of its own utterance.
# --------------------------------------------------------------------------------------
EP0_LINES = [
    ("e01", "This is what a normal day looked like."),
    ("e02", "I didn't know it yet."),
    ("e03", "My alarm went off at seven, and I hit snooze twice."),
    ("e04", "I brushed my teeth in the same mirror, with the same face."),
    ("e05", "I walked to the bus stop past the same houses."),
    ("e06", "The same cat was on the same fence."),
    ("e07", "Afternoon cartoons, and a city name I had never heard of."),
    ("e08", "I changed the channel."),
    ("e09", "That night I left my window open."),
    ("e10", "Someone was standing under the streetlight, waiting for a friend."),
]

EP0 = dict(
    slug="mikay-ep0",
    title_badge="MIKAY",
    title_big="THE DAY BEFORE",
    end_card=dict(big="DAY 1.", small="THEY'RE OUTSIDE."),
    end_hold=3.2,
    lead_in=1.5,            # the title card plays over silence; narration starts after it
    animated=True,
    narration=[dict(id=i, audio=f"{i}.mp3", text=t) for i, t in EP0_LINES],
)

FILMS = {"day0": DAY0, "day1": DAY1, "ep0": EP0}
DEFAULT_FILM = "day0"


def film(key=None):
    return FILMS[key or DEFAULT_FILM]


PRE_FRAMES = {"p1-morning.png", "p1b-alarm.png", "p2-bathroom.png", "p3-street.png",
              "p4-tv.png", "p5-porch.png", "p6-night.png"}


def frame_path(name):
    """Day-0 plates live in art/pre/, day-1 plates in art/frames/."""
    if os.path.exists(os.path.join(FRAMES, name)):
        return os.path.join(FRAMES, name)
    return os.path.join(PRE, name)


def media_duration(path, ffmpeg):
    p = subprocess.run([ffmpeg, "-hide_banner", "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


def build_timeline(spec, ffmpeg):
    """Returns (segments, total_seconds). Each segment carries absolute start/end.

    `lead_in` shifts everything by the length of the title card, in BOTH the audio
    builder and the video builder, so picture, voice and caption share one clock.
    """
    timeline, t = [], float(spec.get("lead_in", 0.0))
    for seg in spec["narration"]:
        seg = dict(seg)
        dur = media_duration(os.path.join(AUDIO, seg["audio"]), ffmpeg)
        seg["start"] = t
        seg["audio_dur"] = dur
        seg["duration"] = dur + TAIL
        timeline.append(seg)
        t += seg["duration"]
    return timeline, t + spec["end_hold"]

"""Shot list + animation for the MIKAY episodes.

Every shot owns one background plate, one 16:9 crop of that plate, and one draw()
function of local shot time t (seconds).  The draw function animates the rig:
walk cycles, breathing, blinks, mouth flaps, gestures, ponytail swing.

Placement rule
--------------
A shot's crop is *not* the same as its neighbours, so frame coordinates never
transfer. Author every position in PLATE coordinates and convert with Shot.pt().
The rig itself is scaled by `k` (the crop's zoom) so she stays the same size
relative to the room she is standing in.

    shots = assign_durations(build_ep0("art"), timeline)
    img = shots[i].frame(t_local)        # -> 1920x1080 RGB
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

import mikay_rig as R

W, H = 1920, 1080
PLATE_W, PLATE_H = 1376, 768

BEDROOM = "bg/bg1-bedroom.png"
BATHROOM = "bg/bg2-bathroom.png"
STREET = "bg/bg3-street.png"
LIVING = "bg/bg4-livingroom.png"
PORCH = "bg/bg5-porch.png"
NIGHT = "bg/bg6-night.png"


# ------------------------------------------------------------------------ helpers
def clip01(x):
    return max(0.0, min(1.0, x))


def ease(x):
    return x * x * (3 - 2 * x)


def breathe(pose, t, amount=1.0):
    """Chest rise + weight shift + head float, so a held pose is never dead."""
    v = math.sin(t * 1.9)
    w = math.sin(t * 0.9 + 0.7)
    pose = dict(pose)
    pose["shoulder"] = (pose["shoulder"][0] + 2.4 * w * amount,
                        pose["shoulder"][1] + 4.0 * v * amount)
    pose["head"] = (pose["head"][0] + 2.2 * w * amount,
                    pose["head"][1] + 5.5 * v * amount)
    pose["hip"] = (pose["hip"][0] + 1.2 * w * amount, pose["hip"][1])
    pose["head_tilt"] = pose.get("head_tilt", 0.0) + 2.2 * w * amount
    pose["ponytail_swing"] = pose.get("ponytail_swing", 0.0) + 6.0 * v * amount
    return pose


def talk(pose, t, rate=2.6, amount=1.0):
    """Mouth flap: fast enough to read as speech, with irregular amplitude."""
    v = math.sin(t * rate * 2 * math.pi) * 0.5 + 0.5
    v *= 0.55 + 0.45 * (math.sin(t * 1.7) * 0.5 + 0.5)
    pose = dict(pose)
    pose["mouth"] = clip01(v * amount)
    if pose["mouth"] > 0.02:
        pose["face"] = "neutral"
    return pose


def blink_at(t, at, dur=0.16):
    """1.0 while the eyes are shut, 0.0 otherwise."""
    return clip01(1.0 - abs(t - at) / (dur * 0.5))


def crop16(cx, cy, width):
    """A strict 16:9 window centred on (cx, cy), clamped inside the plate."""
    width = min(width, PLATE_W)
    h = width * 9 / 16
    if h > PLATE_H:
        h = PLATE_H
        width = h * 16 / 9
    x0 = max(0, min(PLATE_W - width, cx - width / 2))
    y0 = max(0, min(PLATE_H - h, cy - h / 2))
    return (int(x0), int(y0), int(x0 + width), int(y0 + h))


class Shot:
    """One background plate + one 16:9 crop + one draw() of local shot time."""

    def __init__(self, bg_path, duration, draw_fn, crop=None, occluder=None):
        src = Image.open(bg_path).convert("RGB")
        self.crop = crop
        if crop:
            src = src.crop(crop)
        self.bg = src.resize((W, H), Image.LANCZOS)
        self.k = W / (crop[2] - crop[0]) if crop else W / src.width
        self.ox, self.oy = (crop[0], crop[1]) if crop else (0, 0)
        self.duration = duration
        self.draw_fn = draw_fn
        # occluder polygon authored in PLATE coordinates, mapped into the frame
        self.occluder = ([self.pt(x, y) for x, y in occluder] if occluder else None)
        if self.occluder:
            m = Image.new("L", (W, H), 0)
            ImageDraw.Draw(m).polygon(self.occluder, fill=255)
            m = m.filter(ImageFilter.GaussianBlur(1.5))
            self.mask = m

    def place(self, x, y, h_frame):
        """Frame position + rig scale for a character standing at plate (x, y).

        The plates are wide establishing shots, so the character is composited at a
        chosen *screen* height (like any 2D cut-out sitting in front of a backdrop).
        Plate coords decide WHERE she stands; h_frame decides how big she reads.
        """
        fx, fy = self.pt(x, y)
        # draw_character supersamples by R.SS before scaling
        return fx, fy, h_frame / (R.HEIGHT * R.SS)

    def pt(self, x, y):
        """Plate coordinates -> frame coordinates."""
        return ((x - self.ox) * self.k, (y - self.oy) * self.k)

    def frame(self, t):
        canvas = self.bg.convert("RGBA")
        canvas = self.draw_fn(canvas, t, self)
        if self.occluder:
            canvas.paste(self.bg, (0, 0), self.mask)
        return canvas.convert("RGB")


# ------------------------------------------------------------------------ shots
def shot_wake(art_root, dur):
    """Bedroom, morning. She comes out of a stretch and stands, breathing."""
    def draw(canvas, t, shot):
        pose = R.blend_pose(R.pose_stretch(0.2), R.pose_standing(),
                            ease(clip01((t - 0.25) / 1.0)))
        pose = breathe(pose, t, 0.8)
        pose["blink"] = 0.9 if t < 0.35 else blink_at(t, shot.duration * 0.62, 0.22)
        pose["ponytail_swing"] = 5 * math.sin(t * 1.5)
        x, y, sc = shot.place(700, 712, 470)
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc)
        return canvas
    return Shot(f"{art_root}/{BEDROOM}", dur, draw, crop=crop16(720, 520, 760))


def shot_alarm(art_root, dur):
    """Close on the alarm clock: the bells shake, the ring pulses outward."""
    def draw(canvas, t, shot):
        shake = 2.6 * math.sin(t * 40.0)
        x, y = shot.pt(96, 470)
        d = ImageDraw.Draw(canvas)
        ring = 24 * shot.k
        for k in range(3):
            ph = (t * 1.5 + k / 3.0) % 1.0
            r = ring * (0.7 + 1.8 * ph)
            d.arc([x - r + shake, y - r, x + r + shake, y + r], 205, 335,
                  fill=(255, 238, 176, int(140 * (1 - ph))), width=max(2, int(3 * shot.k)))
        return canvas
    return Shot(f"{art_root}/{BEDROOM}", dur, draw, crop=crop16(190, 470, 460))


def shot_close(art_root, dur):
    """Cut-in on her face in the bedroom: she is only just awake."""
    def draw(canvas, t, shot):
        pose = R.pose_standing()
        pose["face"] = "neutral"
        pose["brow"] = 0.45
        pose = breathe(pose, t, 1.5)
        pose["blink"] = blink_at(t, shot.duration * 0.55, 0.26)
        pose["head_tilt"] = 2.5 - 2.0 * math.sin(t * 0.7)
        pose["ponytail_swing"] = 2.5 * math.sin(t * 1.1)
        x, y, sc = shot.place(700, 742, 760)
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc)
        return canvas
    return Shot(f"{art_root}/{BEDROOM}", dur, draw, crop=crop16(700, 500, 620))


def shot_bath(art_root, dur):
    """Bathroom: brushing her teeth at the sink, the tap running."""
    def draw(canvas, t, shot):
        pose = R.pose_brush(t)
        pose = breathe(pose, t, 0.7)
        pose["mouth"] = 0.30 + 0.30 * (math.sin(t * 5.5) * 0.5 + 0.5)
        pose["blink"] = blink_at(t, shot.duration * 0.55, 0.2)
        x, y, sc = shot.place(430, 726, 620)
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc)
        # a thin thread of water from the spout into the basin
        d = ImageDraw.Draw(canvas)
        tx, ty = shot.pt(378, 470)
        for k in range(5):
            ph = (t * 3.2 + k * 0.2) % 1.0
            sy = ty + ph * 46 * shot.k
            d.line([(tx - 2.5 * shot.k, sy), (tx + 2.5 * shot.k, sy + 12 * shot.k)],
                   fill=(196, 232, 250, 170), width=max(1, int(2.0 * shot.k)))
        return canvas
    return Shot(f"{art_root}/{BATHROOM}", dur, draw, crop=crop16(470, 560, 800))


def shot_walk(art_root, dur):
    """Wide street: she walks the sidewalk toward the bus stop, full stride cycle."""
    def draw(canvas, t, shot):
        pose = R.pose_walk(t * 5.2)
        pose = breathe(pose, t, 0.5)
        pose["blink"] = blink_at(t, shot.duration * 0.5, 0.2)
        x, y, sc = shot.place(230, 632, 300)
        x = x + 300 * shot.k * ease(clip01(t / max(0.7, shot.duration * 0.9)))
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc)
        return canvas
    return Shot(f"{art_root}/{STREET}", dur, draw, crop=crop16(560, 520, 1050))


def draw_cat(canvas, x, y, h, tail=0.0):
    """A ginger cat sitting on a rail: haunch, chest, front paws, curled tail."""
    d = ImageDraw.Draw(canvas)
    ink = (30, 24, 30, 255)
    fur = (226, 150, 72, 255)
    light = (246, 194, 126, 255)
    lw = max(2, int(h * 0.070))
    # tail, behind everything, curling up off the rail
    d.line([(x - h * 0.24, y - h * 0.06),
            (x - h * 0.48, y - h * 0.08 + tail * 0.6),
            (x - h * 0.56, y - h * 0.30 + tail),
            (x - h * 0.44, y - h * 0.44 + tail * 1.4)],
           fill=fur, width=max(5, int(h * 0.14)), joint="curve")
    # haunch (back) and chest (front): two rounded masses, no triangle
    d.ellipse([x - h * 0.34, y - h * 0.42, x + h * 0.10, y + h * 0.02], fill=fur,
              outline=ink, width=lw)
    d.ellipse([x - h * 0.12, y - h * 0.46, x + h * 0.30, y + h * 0.02], fill=fur,
              outline=ink, width=lw)
    d.ellipse([x + h * 0.02, y - h * 0.30, x + h * 0.24, y + h * 0.01], fill=light)
    # front legs / paws
    for px in (0.04, 0.20):
        d.line([(x + h * px, y - h * 0.16), (x + h * (px + 0.01), y + h * 0.01)],
               fill=ink, width=max(3, int(h * 0.06)))
        d.ellipse([x + h * (px - 0.04), y - h * 0.02, x + h * (px + 0.07), y + h * 0.05],
                  fill=fur, outline=ink, width=max(2, int(lw * 0.7)))
    # head
    cx, cy, r = x + h * 0.15, y - h * 0.72, h * 0.215
    for sx in (-0.80, 0.80):
        d.polygon([(cx + sx * r - r * 0.40, cy - r * 0.34),
                   (cx + sx * r * 1.34, cy - r * 1.22),
                   (cx + sx * r * 0.60, cy - r * 0.24)], fill=fur, outline=ink)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fur, outline=ink, width=lw)
    for ex in (-0.34, 0.30):
        d.ellipse([cx + ex * r - r * 0.16, cy - r * 0.16,
                   cx + ex * r + r * 0.16, cy + r * 0.14], fill=ink)
    d.polygon([(cx + r * 0.02, cy + r * 0.22), (cx + r * 0.16, cy + r * 0.22),
               (cx + r * 0.09, cy + r * 0.36)], fill=ink)
    return canvas


def shot_cat(art_root, dur):
    """Down the street the cat is on the fence, exactly where it always is."""
    def draw(canvas, t, shot):
        pose = R.pose_standing()
        pose["face"] = "happy"
        pose = breathe(pose, t * 0.9)
        pose["blink"] = blink_at(t, shot.duration * 0.45, 0.2)
        pose["head_tilt"] = 6
        x, y, sc = shot.place(690, 690, 520)
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc)
        cx, cy = shot.pt(1012, 438)
        draw_cat(canvas, cx, cy, 86, tail=2.6 * math.sin(t * 2.2))
        return canvas
    return Shot(f"{art_root}/{STREET}", dur, draw, crop=crop16(960, 470, 800))


# the front lip of the sofa seat in bg4 (plate coords); everything below it hides her legs
SOFA_POLY = [(856, 536), (960, 558), (1106, 586), (1106, 768), (856, 768)]


def shot_sofa(art_root, dur, reach=False):
    """Sitting on the sofa, talking at the television; one beat reaches for the remote."""
    def draw(canvas, t, shot):
        pose = R.pose_sit()
        pose["face"] = "happy"
        pose = breathe(pose, t, 0.7)
        pose = talk(pose, t, rate=2.3, amount=1.0)
        pose["blink"] = blink_at(t, shot.duration * 0.6, 0.2)
        if not reach:
            # a small gesture on the beat
            g = math.sin(t * 2.1)
            pose["arm_l"] = [pose["arm_l"][0],
                             (pose["arm_l"][1][0] - 3 * g, pose["arm_l"][1][1] + 5 * g),
                             (pose["arm_l"][2][0] - 5 * g, pose["arm_l"][2][1] + 8 * g)]
        if reach:
            k = ease(clip01(t / 0.7))
            hand = pose["arm_r"][2]
            target = (hand[0] + 54, hand[1] + 14)
            pose["arm_r"] = [pose["arm_r"][0],
                             R.ik2(pose["arm_r"][0], target, R.UPPER_ARM, R.FOREARM, bend=1),
                             R.lerp_pt(hand, target, k)]
            pose["mouth"] = 0.0
        # seated on the sofa, feet on the floor in front of the seat
        x, y, sc = shot.place(1000, 636, 450)
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc, lift=0)
        return canvas
    return Shot(f"{art_root}/{LIVING}", dur, draw, crop=crop16(1000, 540, 860))


# the blanket line in bg6 (plate coords): she is sitting up behind it
NIGHT_BED = [(150, 486), (330, 470), (540, 486), (760, 536), (760, 768), (150, 768)]


def shot_night(art_root, dur, worried=False):
    """Night. She sits up in bed; outside the window the streetlight is on."""
    def draw(canvas, t, shot):
        pose = R.pose_lie(t)
        pose["face"] = "worried" if worried else "happy"
        pose["brow"] = 0.7 if worried else 0.0
        pose = breathe(pose, t, 1.25)
        pose["blink"] = blink_at(t, shot.duration * 0.5, 0.22)
        # she turns her head toward the window, then back
        look = math.sin(t * 0.85) * 0.5 + 0.5
        pose["head_tilt"] = 3.0 - 7.0 * look
        pose["mouth"] = 0.0
        if worried:
            pose["sweat"] = clip01((t - 1.2) / 0.9)
            pose["brow"] = 0.7
            pose["mouth"] = 0.18 * clip01((t - 1.6) / 0.6)
        x, y, sc = shot.place(450, 520, 430)
        ch, a = R.draw_character(pose, scale=sc)
        R.paste_at(canvas, ch, a, x, y, sc, shadow=False)
        return canvas
    crop = crop16(600, 400, 700) if worried else crop16(520, 400, 620)
    return Shot(f"{art_root}/{NIGHT}", dur, draw, crop=crop, occluder=NIGHT_BED)


def shot_window(art_root, dur):
    """Out the bedroom window: the streetlamp, and someone standing under it."""
    def draw(canvas, t, shot):
        fx, fy = shot.pt(1290, 330)
        s = 1.25 * shot.k
        ink = (12, 14, 26, 235)
        sway = math.sin(t * 0.9) * 2.6 * s
        hd = fy - 74 * s
        d = ImageDraw.Draw(canvas)
        d.ellipse([fx - 8 * s + sway, hd - 14 * s, fx + 8 * s + sway, hd + 2 * s], fill=ink)
        d.line([(fx + sway, hd + 2 * s), (fx + sway * 0.6, fy - 26 * s)], fill=ink,
               width=max(3, int(9 * s)))
        d.line([(fx - 13 * s + sway, fy), (fx + sway * 0.6, fy - 26 * s)], fill=ink,
               width=max(3, int(5 * s)))
        d.line([(fx + 13 * s + sway, fy), (fx + sway * 0.6, fy - 26 * s)], fill=ink,
               width=max(3, int(5 * s)))
        d.line([(fx - 11 * s + sway, hd + 12 * s), (fx - 16 * s + sway, fy - 40 * s)],
               fill=ink, width=max(3, int(5 * s)))
        d.line([(fx + 11 * s + sway, hd + 12 * s), (fx + 16 * s + sway, fy - 40 * s)],
               fill=ink, width=max(3, int(5 * s)))
        # the lamp itself breathes a little
        d = ImageDraw.Draw(canvas)
        lx, ly = shot.pt(1196, 236)
        a = 26 + 14 * (math.sin(t * 3.1) * 0.5 + 0.5)
        d.ellipse([lx - 26 * shot.k, ly - 10 * shot.k, lx + 26 * shot.k, ly + 12 * shot.k],
                  fill=(255, 226, 150, int(a)))
        return canvas
    return Shot(f"{art_root}/{NIGHT}", dur, draw, crop=crop16(1150, 250, 460))


# ------------------------------------------------------------------------ assembly
def build_ep0(art_root):
    """One shot per narration line, in order. Durations filled in by assign_durations."""
    return [
        shot_wake(art_root, 0),              # e01 this is what a normal day looked like
        shot_close(art_root, 0),             # e02 I didn't know it yet
        shot_alarm(art_root, 0),             # e03 alarm went off at seven
        shot_bath(art_root, 0),              # e04 brushed my teeth
        shot_walk(art_root, 0),              # e05 walked to the bus stop
        shot_cat(art_root, 0),               # e06 the same cat on the same fence
        shot_sofa(art_root, 0),              # e07 afternoon cartoons
        shot_sofa(art_root, 0, reach=True),  # e08 I changed the channel
        shot_night(art_root, 0),             # e09 that night I left my window open
        shot_window(art_root, 0),            # e10 someone was standing there
    ]


def assign_durations(shots, timeline):
    """Bind each shot's clock to its own utterance: one shot per narration line."""
    if len(shots) != len(timeline):
        raise ValueError(f"{len(shots)} shots for {len(timeline)} narration lines")
    for shot, seg in zip(shots, timeline):
        shot.duration = seg["duration"]
    return shots

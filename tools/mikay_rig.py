"""Mikay — a hand-built 2D rig for the stick-figure heroine.

The rig is drawn in *local character space*: origin between the feet, +y points UP,
units are roughly pixels at scale 1.0, and the whole figure is about 307 units tall.
Every frame re-draws the character from a pose dict, which is what makes her animate
(walk cycles, blinks, mouth flaps, breathing) instead of sliding a still around.

Public API
----------
base_pose()                        -> neutral standing pose
pose_standing() / pose_stretch(t) / pose_walk(phase, speed=1)
pose_sit() / pose_sit_slouch() / pose_brush(t) / pose_lie(t) / pose_porch(t)
blend_pose(a, b, t)                -> interpolate two poses
ik2(root, target, l1, l2, bend=1)  -> two-bone IK, returns the joint
draw_character(pose, scale=1.0)    -> (RGBA image, anchor point)
paste_at(canvas, char, anchor, x, y, scale, shadow=True)

Pose keys
---------
hip, shoulder, head, head_tilt,
leg_l / leg_r : [hip, knee, ankle]
arm_l / arm_r : [shoulder, elbow, hand]
face: "neutral" | "happy" | "worried" | "surprised" | "sleepy"
blink (0..1), mouth (0..1 open), brow (-1..1), sweat (0..1),
ponytail_swing (degrees), squash (vertical squash, 1.0 = none)
"""
import math

from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersample factor for anti-aliased ink lines

INK = (18, 16, 20, 255)
INK_SOFT = (44, 38, 46, 255)
HEAD_FILL = (252, 250, 247, 255)
HOODIE = (179, 48, 90, 255)
HOODIE_DARK = (126, 30, 60, 255)
HOODIE_LIGHT = (208, 84, 122, 255)
SKIRT = (46, 46, 56, 255)
SKIRT_DARK = (32, 32, 40, 255)
WHITE = (255, 255, 255, 255)
HAIR = (22, 19, 24, 255)
HAIR_LIGHT = (52, 46, 56, 255)
BAND = (226, 52, 106, 255)
BLUSH = (240, 148, 158, 90)

# ---- skeleton proportions (local units, y up, floor at y = 0) ------------------------
# matched to art/mikay-character-sheet.png: head ~1/4 of height, long thin legs
R_HEAD = 44
HEAD_Y = 296
SHOULDER_Y = 240
HIP_Y = 150
THIGH = 66
SHIN = 74
UPPER_ARM = 58
FOREARM = 54
LEG_W = 8.5
ARM_W = 7.5

# fixed drawing box, so the anchor never jitters between frames
BOX = (-190, 190, -18, 356)  # minx, maxx, miny, maxy
HEIGHT = 356  # local units from the floor to the top of the head


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_pt(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def ik2(root, target, l1, l2, bend=1):
    """Two-bone IK: returns the joint between `root` and `target`.

    bend=+1 puts the joint on one side of the root->target line, -1 on the other.
    """
    dx, dy = target[0] - root[0], target[1] - root[1]
    dist = math.hypot(dx, dy)
    dist = max(1e-3, min(dist, (l1 + l2) * 0.999))
    a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    ux, uy = dx / dist, dy / dist
    mx, my = root[0] + ux * a, root[1] + uy * a
    return (mx - uy * h * bend, my + ux * h * bend)


# --------------------------------------------------------------------------- poses
def base_pose():
    return dict(
        skirt_len=50,
        hip=(0, HIP_Y), shoulder=(0, SHOULDER_Y), head=(0, HEAD_Y), head_tilt=0.0,
        leg_l=[(0, HIP_Y), (0, HIP_Y - THIGH), (0, 6)],
        leg_r=[(0, HIP_Y), (0, HIP_Y - THIGH), (0, 6)],
        arm_l=[(0, SHOULDER_Y), (0, SHOULDER_Y - UPPER_ARM), (0, SHOULDER_Y - UPPER_ARM - FOREARM + 4)],
        arm_r=[(0, SHOULDER_Y), (0, SHOULDER_Y - UPPER_ARM), (0, SHOULDER_Y - UPPER_ARM - FOREARM + 4)],
        face="neutral", blink=0.0, mouth=0.0, brow=0.0, sweat=0.0,
        ponytail_swing=0.0, squash=1.0,
    )


def _mirror_leg(hip, dx, dy):
    """Leg from a hip point, knee and ankle offset relative to it."""
    return [hip, (hip[0] + dx, hip[1] + dy[0]), (hip[0] + dx * 1.15, hip[1] + dy[1])]


def pose_standing():
    p = base_pose()
    p["leg_l"] = [(-11, HIP_Y), (-13, HIP_Y - THIGH), (-15, 12)]
    p["leg_r"] = [(11, HIP_Y), (13, HIP_Y - THIGH), (15, 12)]
    p["arm_l"] = [(-28, SHOULDER_Y - 6), (-40, 186), (-42, 130)]
    p["arm_r"] = [(28, SHOULDER_Y - 6), (40, 186), (42, 130)]
    return p


def pose_stretch(t):
    """A big morning stretch: arms overhead, spine arched, ponytail swinging."""
    p = base_pose()
    sway = math.sin(t * 1.6)
    p["leg_l"] = [(-11, HIP_Y), (-14, HIP_Y - THIGH), (-16, 12)]
    p["leg_r"] = [(11, HIP_Y), (14, HIP_Y - THIGH), (16, 12)]
    lift = 20 + 5 * sway
    p["arm_l"] = [(-28, SHOULDER_Y + lift), (-52, 300 + lift * 0.4), (-40, 340 + lift * 0.3)]
    p["arm_r"] = [(28, SHOULDER_Y + lift), (52, 300 + lift * 0.4), (40, 340 + lift * 0.3)]
    p["head"] = (0, HEAD_Y + 6)
    p["face"] = "happy"
    p["mouth"] = 0.35 + 0.15 * sway
    p["blink"] = 0.85
    p["ponytail_swing"] = 6 * sway
    return p


def pose_walk(phase, speed=1.0):
    """One full stride per 2*pi of phase. Feet plant, knees bend, arms counter-swing."""
    p = base_pose()
    a = math.sin(phase)
    b = math.cos(phase)
    stride = 32 * speed
    lift = 18 * speed
    p["leg_l"] = [(-9, HIP_Y),
                  (-9 + stride * 0.55 * a, HIP_Y - THIGH + max(0.0, -b) * lift * 0.7),
                  (-9 + stride * a, 12 + max(0.0, b) * lift)]
    p["leg_r"] = [(9, HIP_Y),
                  (9 - stride * 0.55 * a, HIP_Y - THIGH + max(0.0, b) * lift * 0.7),
                  (9 - stride * a, 12 + max(0.0, -b) * lift)]
    p["arm_l"] = [(-28, SHOULDER_Y - 6),
                  (-34 - 12 * a, 186 - 6 * a),
                  (-32 - 24 * a, 130 - 10 * a)]
    p["arm_r"] = [(28, SHOULDER_Y - 6),
                  (34 + 12 * a, 186 + 6 * a),
                  (32 + 24 * a, 130 + 10 * a)]
    p["hip"] = (0, HIP_Y + abs(b) * 3.0)          # gentle bob
    p["shoulder"] = (0, SHOULDER_Y + abs(b) * 3.0)
    p["head"] = (0, HEAD_Y + abs(b) * 3.0)
    p["ponytail_swing"] = 5 * a
    return p


def pose_sit():
    """Seated: thighs forward, shins down, hands resting on the lap."""
    p = base_pose()
    # knees forward, shins hanging: reads as "sitting" even from the front
    p["hip"] = (0, 168)
    p["leg_l"] = [(-13, 168), (14, 150), (17, 62)]
    p["leg_r"] = [(13, 168), (32, 150), (35, 62)]
    p["skirt_len"] = 44
    p["shoulder"] = (0, 254)
    p["head"] = (0, 310)
    p["arm_l"] = [(-26, 248), (-26, 206), (-8, 176)]
    p["arm_r"] = [(26, 248), (26, 206), (8, 176)]
    return p


def pose_sit_slouch():
    p = pose_sit()
    p["shoulder"] = (0, 236)
    p["head"] = (2, 290)
    p["head_tilt"] = 6
    p["face"] = "sleepy"
    p["arm_l"] = [(-26, 232), (-26, 192), (-8, 168)]
    p["arm_r"] = [(26, 232), (26, 192), (10, 168)]
    return p


def pose_brush(t):
    """Brushing her teeth: one hand up at the mouth, scrubbing in little circles."""
    p = pose_standing()
    scrub = math.sin(t * 9.0)
    head_hand = (14 + 3 * scrub, 276 + 4 * scrub)
    p["arm_r"] = [p["arm_r"][0],
                  ik2(p["arm_r"][0], head_hand, UPPER_ARM, FOREARM, bend=-1),
                  head_hand]
    p["arm_l"] = [(-28, SHOULDER_Y - 6), (-38, 186), (-24, 158)]
    p["head_tilt"] = 3 * math.sin(t * 2.2)
    p["ponytail_swing"] = 3 * math.sin(t * 3.0)
    return p


def pose_lie(t):
    """Sitting up in bed: shoulders low, legs foreshortened under the blanket."""
    p = base_pose()
    p["hip"] = (0, 130)
    p["shoulder"] = (0, 214)
    p["head"] = (0, 270)
    p["skirt_len"] = 44
    p["leg_l"] = [(-9, 130), (28, 132), (32, 96)]
    p["leg_r"] = [(9, 130), (46, 132), (50, 96)]
    p["arm_l"] = [(-26, 208), (-32, 170), (-14, 146)]
    p["arm_r"] = [(26, 208), (32, 170), (14, 146)]
    p["head_tilt"] = 2 * math.sin(t * 1.1)
    return p


def pose_porch(t):
    """Standing on the porch, hands loose, hair moving in the evening air."""
    p = pose_standing()
    p["arm_l"] = [(-28, SHOULDER_Y - 6), (-40, 188), (-30, 156)]
    p["arm_r"] = [(28, SHOULDER_Y - 6), (40, 188), (26, 152)]
    p["head_tilt"] = 4 + 3 * math.sin(t * 0.9)
    p["ponytail_swing"] = 6 * math.sin(t * 1.4)
    p["face"] = "happy"
    return p


def blend_pose(a, b, t):
    """Linear blend of two poses (points, scalars, discrete face states)."""
    out = dict(a)
    for k, va in a.items():
        vb = b.get(k, va)
        if isinstance(va, tuple):
            out[k] = lerp_pt(va, vb, t)
        elif isinstance(va, list):
            out[k] = [lerp_pt(pa, pb, t) for pa, pb in zip(va, vb)]
        elif isinstance(va, (int, float)) and not isinstance(va, bool):
            out[k] = lerp(va, vb, t)
    if t >= 0.5:
        out["face"] = b.get("face", a["face"])
    return out


# --------------------------------------------------------------------------- drawing
def _stroke(d, pts, fill, width):
    """A polyline with round joints, so limbs never show a gap at the knee/elbow."""
    w = max(1, int(round(width)))
    d.line(pts, fill=fill, width=w, joint="curve")
    for p in pts:
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=fill)


def _taper(d, pts, widths, fill, outline=None, ow=0):
    """A tapered ribbon through `pts` — used for the ponytail."""
    left, right = [], []
    for i, p in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - p[0], pts[1][1] - p[1]
        elif i == len(pts) - 1:
            dx, dy = p[0] - pts[-2][0], p[1] - pts[-2][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n, dx / n
        w = widths[i] / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    poly = left + right[::-1]
    if outline:
        d.polygon(poly, fill=outline)
        shrink = ow
        inner = [((x + cx) / 2, (y + cy) / 2) for (x, y), (cx, cy) in
                 zip(poly, [pts[len(pts) // 2]] * len(poly))]
        poly2 = [((x - pic[0]) * (1 - shrink) + pic[0], (y - pic[1]) * (1 - shrink) + pic[1])
                 for (x, y), pic in zip(poly, inner)]
        d.polygon(poly2, fill=fill)
    else:
        d.polygon(poly, fill=fill)
    return poly


def _shoe(d, ankle, facing, foot_dir, k=1.0):
    """A chunky sneaker: black upper, white sole, always flat on the ground."""
    x, y = ankle
    w, h = 26 * k, 15 * k
    toe = 1 if foot_dir >= 0 else -1
    body = [(x - w * 0.5, y + h * 0.05), (x + w * 0.5, y + h * 0.05),
            (x + w * 0.5 + toe * 8 * k, y + h * 0.6), (x - w * 0.5 + toe * 8 * k, y + h * 0.6)]
    d.polygon(body, fill=INK)
    d.ellipse([x - w * 0.5, y - h * 0.35, x + w * 0.5, y + h * 0.30], fill=INK)
    d.line([(x - w * 0.55 + toe * 7 * k, y + h * 0.66), (x + w * 0.6 + toe * 7 * k, y + h * 0.66)],
           fill=WHITE, width=int(4.5 * k))


def _hand(d, p, r=7.5, k=1.0):
    r = r * k
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=WHITE, outline=INK,
              width=int(r * 0.42))


def draw_character(pose, scale=1.0, ss=SS):
    """Render a pose to a transparent RGBA sprite. Returns (image, anchor)."""
    minx, maxx, miny, maxy = BOX
    s = ss
    img = Image.new("RGBA", (int((maxx - minx) * s), int((maxy - miny) * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def T(p):
        return ((p[0] - minx) * s, (maxy - p[1]) * s)

    def P(p):
        return T(p)

    lw = 5.2 * s
    head_c = pose["head"]
    tilt = math.radians(pose.get("head_tilt", 0.0))

    def H(p):
        """Head-local point (x right, y up, origin at head centre) with the tilt applied."""
        x, y = p
        return T((head_c[0] + x * math.cos(tilt) - y * math.sin(tilt),
                  head_c[1] + x * math.sin(tilt) + y * math.cos(tilt)))

    # ---- ponytail (behind everything) ------------------------------------------------
    swing = math.radians(pose.get("ponytail_swing", 0.0))
    tie = H((R_HEAD * 0.52, R_HEAD * 0.50))
    tail = [
        tie,
        H((R_HEAD * 0.98, R_HEAD * 0.16 + 5 * math.sin(swing))),
        H((R_HEAD * 1.24, -R_HEAD * 0.60 + 12 * math.sin(swing))),
        H((R_HEAD * 1.16, -R_HEAD * 1.45 + 20 * math.sin(swing))),
        H((R_HEAD * 0.82, -R_HEAD * 2.10 + 24 * math.sin(swing))),
        H((R_HEAD * 0.42, -R_HEAD * 2.40 + 20 * math.sin(swing))),
    ]
    widths = [15 * s, 27 * s, 28 * s, 22 * s, 12 * s, 2 * s]
    _taper(d, tail, widths, HAIR)

    # ---- legs ------------------------------------------------------------------------
    for i, leg in enumerate(("leg_l", "leg_r")):
        pts = [P(p) for p in pose[leg]]
        _stroke(d, pts, INK, LEG_W * s)
        _shoe(d, pts[-1], facing=1, foot_dir=1, k=s)

    # ---- skirt -----------------------------------------------------------------------
    hip = P(pose["hip"])
    sh = P(pose["shoulder"])
    hem_y = hip[1] + pose.get("skirt_len", 50) * s
    waist = 26 * s
    flare = 40 * s
    skirt = [(hip[0] - waist, hip[1] - 24 * s), (hip[0] + waist, hip[1] - 24 * s),
             (hip[0] + flare, hem_y), (hip[0] - flare, hem_y)]
    d.polygon(skirt, fill=SKIRT)
    for i in range(-2, 3):
        x0 = hip[0] + i * 12 * s
        x1 = hip[0] + i * 21 * s
        d.line([(x0, hip[1] - 22 * s), (x1, hem_y - 2 * s)], fill=SKIRT_DARK,
               width=int(2.4 * s))
    d.line([(hip[0] - flare, hem_y), (hip[0] + flare, hem_y)], fill=INK, width=int(lw * 0.8))
    d.line([(hip[0] - waist, hip[1] - 26 * s), (hip[0] - flare + 4 * s, hem_y)], fill=INK,
           width=int(lw * 0.7))
    d.line([(hip[0] + waist, hip[1] - 26 * s), (hip[0] + flare - 4 * s, hem_y)], fill=INK,
           width=int(lw * 0.7))

    # ---- hoodie body -----------------------------------------------------------------
    d.ellipse([sh[0] - 25 * s, sh[1] - 12 * s, sh[0] + 25 * s, sh[1] + 14 * s],
              fill=HOODIE_DARK, outline=INK, width=int(lw * 0.75))
    torso = [
        (sh[0] - 29 * s, sh[1] + 6 * s),
        (sh[0] + 29 * s, sh[1] + 6 * s),
        (sh[0] + 33 * s, sh[1] - 52 * s),
        (hip[0] + 26 * s, hip[1] - 10 * s),
        (hip[0] - 26 * s, hip[1] - 10 * s),
        (sh[0] - 33 * s, sh[1] - 52 * s),
    ]
    d.polygon(torso, fill=HOODIE, outline=INK)
    d.line(torso + [torso[0]], fill=INK, width=int(lw), joint="curve")
    # a fold line across the chest, so the hoodie reads as clothing not a tube
    d.line([(sh[0] - 20 * s, sh[1] - 34 * s), (sh[0] - 6 * s, sh[1] - 40 * s),
            (sh[0] + 16 * s, sh[1] - 33 * s)], fill=HOODIE_DARK, width=int(2.6 * s))
    # drawstrings + pocket
    for dx in (-8, 8):
        d.line([(sh[0] + dx * s, sh[1] - 2 * s), (sh[0] + dx * s, sh[1] - 30 * s)],
               fill=WHITE, width=int(2.6 * s))
        d.ellipse([sh[0] + dx * s - 3 * s, sh[1] - 34 * s, sh[0] + dx * s + 3 * s,
                   sh[1] - 28 * s], fill=WHITE)
    d.line([(hip[0] - 16 * s, hip[1] + 12 * s), (hip[0] + 16 * s, hip[1] + 12 * s)],
           fill=HOODIE_DARK, width=int(3.4 * s))

    # ---- arms -------------------------------------------------------------------------
    for arm in ("arm_l", "arm_r"):
        pts = [P(p) for p in pose[arm]]
        _stroke(d, pts, INK, (ARM_W + 7) * s)          # sleeve
        _stroke(d, pts, HOODIE, (ARM_W + 3) * s)
        cuff = pts[-1]
        d.ellipse([cuff[0] - 7 * s, cuff[1] - 7 * s, cuff[0] + 7 * s, cuff[1] + 7 * s],
                  fill=HOODIE_DARK)
        _hand(d, cuff, k=s)

    # ---- head -------------------------------------------------------------------------
    r = R_HEAD * s
    hc = T(head_c)
    d.ellipse([hc[0] - r, hc[1] - r, hc[0] + r, hc[1] + r],
              fill=HEAD_FILL, outline=INK, width=int(lw * 1.25))

    face = pose.get("face", "neutral")
    blink = max(0.0, min(1.0, pose.get("blink", 0.0)))
    mouth = max(0.0, min(1.0, pose.get("mouth", 0.0)))
    brow = pose.get("brow", 0.0)

    eye_dx = 0.42 * R_HEAD
    eye_y = 0.10 * R_HEAD
    eye_w = 0.20 * R_HEAD
    eye_h = 0.30 * R_HEAD * (1.0 - 0.92 * blink)

    for sgn in (-1, 1):
        ex, ey = sgn * eye_dx, eye_y
        if blink > 0.82:
            a, b = H((ex - eye_w * 0.8, ey)), H((ex + eye_w * 0.8, ey))
            d.line([a, b], fill=INK, width=int(4.2 * s), joint="curve")
            continue
        cx, cy = H((ex, ey))
        d.ellipse([cx - eye_w * s, cy - eye_h * s, cx + eye_w * s, cy + eye_h * s], fill=INK)
        # catch-light
        d.ellipse([cx - eye_w * 0.42 * s, cy - eye_h * 0.62 * s,
                   cx - eye_w * 0.02 * s, cy - eye_h * 0.18 * s], fill=(255, 255, 255, 235))
        # three lashes on the outer corner
        for k in range(3):
            off = (k - 1) * 0.30
            a = H((ex + sgn * eye_w * 0.55, ey + eye_h * (0.55 + off * 0.5)))
            b = H((ex + sgn * (eye_w * 1.35 + 3), ey + eye_h * (0.95 + off * 0.7)))
            d.line([a, b], fill=INK, width=int(3.0 * s))

    # brows
    if abs(brow) > 0.02 or face == "worried":
        lift = 0.62 * R_HEAD + 6 * abs(brow) + (4 if face == "worried" else 0)
        for sgn in (-1, 1):
            inner = H((sgn * 0.30 * R_HEAD, lift - 6 * (1 if face == "worried" else 0)))
            outer = H((sgn * 0.60 * R_HEAD, lift + 5 * (1 if face == "worried" else 0)))
            d.line([inner, outer], fill=INK, width=int(3.4 * s))

    # mouth
    if mouth > 0.06:
        mw, mh = 0.20 * R_HEAD, (0.08 + 0.22 * mouth) * R_HEAD
        mx, my = H((0, -0.34 * R_HEAD))
        d.ellipse([mx - mw * s, my - mh * s, mx + mw * s, my + mh * s],
                  fill=(58, 34, 44, 255), outline=INK, width=int(2.4 * s))
    else:
        if face == "happy":
            a, b, c = H((-0.22 * R_HEAD, -0.28 * R_HEAD)), H((0, -0.40 * R_HEAD)), H((0.22 * R_HEAD, -0.28 * R_HEAD))
            d.line([a, b, c], fill=INK, width=int(3.4 * s), joint="curve")
        elif face == "worried":
            a, b, c = H((-0.20 * R_HEAD, -0.40 * R_HEAD)), H((0, -0.32 * R_HEAD)), H((0.20 * R_HEAD, -0.40 * R_HEAD))
            d.line([a, b, c], fill=INK, width=int(3.4 * s), joint="curve")
        else:
            a, b = H((-0.16 * R_HEAD, -0.34 * R_HEAD)), H((0.16 * R_HEAD, -0.34 * R_HEAD))
            d.line([a, b], fill=INK, width=int(3.8 * s))

    # sweat bead
    if pose.get("sweat", 0) > 0.05:
        sx, sy = H((-0.78 * R_HEAD, 0.60 * R_HEAD))
        rr = 7 * s
        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=(120, 200, 246, 255),
                  outline=INK, width=int(2.2 * s))

    # hair front: a fringe sweeping across the forehead + the tie
    fringe = [H((-1.02 * R_HEAD, 0.36 * R_HEAD)), H((-0.55 * R_HEAD, 1.02 * R_HEAD)),
              H((0.30 * R_HEAD, 1.04 * R_HEAD)), H((0.92 * R_HEAD, 0.55 * R_HEAD)),
              H((0.60 * R_HEAD, 0.86 * R_HEAD)), H((0.02 * R_HEAD, 0.80 * R_HEAD)),
              H((-0.50 * R_HEAD, 0.74 * R_HEAD))]
    d.polygon(fringe, fill=HAIR)
    tie_c = H((R_HEAD * 0.66, R_HEAD * 0.58))
    d.ellipse([tie_c[0] - 9 * s, tie_c[1] - 7 * s, tie_c[0] + 9 * s, tie_c[1] + 7 * s],
              fill=BAND, outline=INK, width=int(2.0 * s))

    if scale != 1.0:
        w = max(1, int(img.width * scale))
        h = max(1, int(img.height * scale))
        img = img.resize((w, h), Image.LANCZOS)
    anchor = ((0 - minx) * s * scale, (maxy - 0) * s * scale)
    return img, anchor


def paste_at(canvas, char, anchor, x, y, scale=1.0, shadow=True, lift=0.0):
    """Drop a rendered character so the joint `lift` local units above the floor is at (x, y).

    lift=0 puts her feet at (x, y); lift=158 puts her hips there (seated poses).
    """
    if shadow:
        w = char.width * 0.46
        h = max(6.0, 13 * scale)
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.ellipse([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=(12, 10, 16, 92))
        sh = sh.filter(ImageFilter.GaussianBlur(5 * scale))
        canvas.alpha_composite(sh)
    py = y + lift * scale
    canvas.alpha_composite(char, (int(round(x - anchor[0])), int(round(py - anchor[1]))))
    return canvas

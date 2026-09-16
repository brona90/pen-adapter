"""Generate the 16 step figures for the bench guide and splice them into the HTML (replacing any present)."""
import re, math

PART = 'style="fill:var(--accent-soft);stroke:currentColor;stroke-width:1.2;stroke-linejoin:round"'
PART2 = 'style="fill:var(--surface-2);stroke:currentColor;stroke-width:1.2;stroke-linejoin:round"'
CAL = 'style="fill:currentColor;opacity:.82"'
RED = 'style="stroke:var(--warn);stroke-width:1.4;fill:none"'
REDF = 'style="fill:var(--warn)"'
MUT = 'style="stroke:var(--muted);stroke-width:1;fill:none"'
TXT = 'style="font:11px var(--mono);fill:currentColor"'
TXTR = 'style="font:600 11px var(--mono);fill:var(--warn)"'
TXTM = 'style="font:10px var(--mono);fill:var(--muted)"'
DEFS = ('<defs><marker id="{id}a" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0 0 L8 4 L0 8 z" style="fill:var(--warn)"/></marker></defs>')

def fig(id_, w, h, body, caption):
    s = (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{caption}" xmlns="http://www.w3.org/2000/svg">'
         + DEFS.format(id=id_) + body + '</svg>')
    return f'<figure class="fig">{s}<figcaption>{caption}</figcaption></figure>'

def P(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"

def zig(a0, a1, root, h, p, out, vertical):
    """Zigzag along one edge from a0 to a1 (axis coordinate); root = cross coordinate."""
    pts, a = [], a0
    while a + p <= a1 + 0.01:
        pts.append((a, root)); pts.append((a + p / 2, root + out * h)); a += p
    pts.append((a1, root))
    return [(y, x) if vertical else (x, y) for x, y in pts]

def rod_v(cx, w, y0, y1, h=6, p=12):
    r = zig(y0, y1, cx + w / 2, h, p, +1, True)
    l = zig(y0, y1, cx - w / 2, h, p, -1, True)[::-1]
    return P(r + l)

def rod_h(x0, x1, cy, w, h=5, p=12):
    top = zig(x0, x1, cy - w / 2, h, p, -1, False)
    bot = zig(x0, x1, cy + w / 2, h, p, +1, False)[::-1]
    return P(top + bot)

def hdim(xa, xb, y, id_, label, ty=None, anchor="middle", tx=None):
    b = f'<line x1="{xa}" y1="{y}" x2="{xb}" y2="{y}" {RED} marker-start="url(#{id_}a)" marker-end="url(#{id_}a)"/>'
    if label:
        b += f'<text x="{tx if tx is not None else (xa+xb)/2}" y="{ty if ty is not None else y+14}" text-anchor="{anchor}" {TXTR}>{label}</text>'
    return b

def vdim(x, y0, y1, id_, label, side=1, ty=None):
    b = f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" {RED} marker-start="url(#{id_}a)" marker-end="url(#{id_}a)"/>'
    if label:
        b += f'<text x="{x + side*8}" y="{ty if ty is not None else (y0+y1)/2+4}" text-anchor="{"start" if side>0 else "end"}" {TXTR}>{label}</text>'
    return b

def ext_h(x0, y, x1): return f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" {MUT} stroke-dasharray="3 2"/>'
def ext_v(x, y0, y1): return f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" {MUT} stroke-dasharray="3 2"/>'

def jaws_down(xa, xb, ybeam, ytip):
    """Outside jaws hanging from a horizontal beam; inner faces at xa/xb, knife tips end at ytip."""
    b = f'<rect x="{xa-22}" y="{ybeam}" width="{xb-xa+44}" height="9" rx="1" {CAL}/>'
    for x, s in ((xa, -1), (xb, +1)):
        b += f'<rect x="{x if s>0 else x-7}" y="{ybeam+9}" width="7" height="{ytip-ybeam-9-16}" {CAL}/>'
        b += f'<polygon points="{x},{ytip-16} {x+s*7},{ytip-16} {x+s*2.5},{ytip} {x},{ytip}" {CAL}/>'
    return b

def jaws_right(ya, yb, xbeam, xtip):
    """Outside jaws from a vertical beam on the left; inner faces at ya/yb, tips end at xtip."""
    b = f'<rect x="{xbeam}" y="{ya-22}" width="9" height="{yb-ya+44}" rx="1" {CAL}/>'
    for y, s in ((ya, -1), (yb, +1)):
        b += f'<rect x="{xbeam+9}" y="{y if s>0 else y-7}" width="{xtip-xbeam-9-16}" height="7" {CAL}/>'
        b += f'<polygon points="{xtip-16},{y} {xtip-16},{y+s*7} {xtip},{y+s*2.5} {xtip},{y}" {CAL}/>'
    return b

def tips_right(ys, xbeam, xtip, ybeam0, ybeam1):
    """Pitch tips: vertical beam, thin tips pointing right onto crests at each y."""
    b = f'<rect x="{xbeam}" y="{ybeam0}" width="9" height="{ybeam1-ybeam0}" rx="1" {CAL}/>'
    for y in ys:
        b += f'<polygon points="{xbeam+9},{y-4} {xbeam+30},{y-1.5} {xtip},{y} {xbeam+30},{y+1.5} {xbeam+9},{y+4}" {CAL}/>'
    return b

def tips_down(xs, ybeam, ytip, xbeam0, xbeam1):
    b = f'<rect x="{xbeam0}" y="{ybeam}" width="{xbeam1-xbeam0}" height="9" rx="1" {CAL}/>'
    for x in xs:
        b += f'<polygon points="{x-4},{ybeam+9} {x-1.5},{ybeam+30} {x},{ytip} {x+1.5},{ybeam+30} {x+4},{ybeam+9}" {CAL}/>'
    return b

def depth_v(x, y_base, y_tip, base_w=40):
    return (f'<rect x="{x-base_w/2}" y="{y_base-7}" width="{base_w}" height="7" rx="1" {CAL}/>'
            f'<rect x="{x-1.5}" y="{y_base-30}" width="3" height="{y_tip-y_base+30}" {CAL}/>')

def depth_h(y, x_base, x_tip, base_h=40):
    return (f'<rect x="{x_base}" y="{y-base_h/2}" width="7" height="{base_h}" rx="1" {CAL}/>'
            f'<rect x="{x_base-30}" y="{y-1.5}" width="{x_tip-x_base+30}" height="3" {CAL}/>')

def section_h(x0, cy):
    """Asvine section, axis horizontal, nib to the right. Returns (svg, dict of key x/y)."""
    k = dict(body0=x0, sh0=x0+70, sh1=x0+78, th0=x0+78, th1=x0+126, nib1=x0+164, cy=cy, r_sh=36, r_th=23)
    b = f'<rect x="{x0}" y="{cy-30}" width="70" height="60" rx="3" {PART}/>'
    b += f'<rect x="{k["sh0"]}" y="{cy-36}" width="8" height="72" {PART}/>'
    b += f'<path d="{rod_h(k["th0"], k["th1"], cy, 46)}" {PART}/>'
    b += f'<path d="M{k["th1"]} {cy-14} L{k["nib1"]} {cy-3} L{k["nib1"]} {cy+3} L{k["th1"]} {cy+14} Z" {PART2}/>'
    return b, k

F = {}
cx = 150

# ---------- A1 / A2 ----------
for sid, xa, xb, label, cap in (
    ("A1", cx-36, cx+36, "A1 · major: crest to crest", "Outside jaw tips land on opposite crests; the reading is the major diameter."),
    ("A2", cx-30, cx+30, "A2 · minor: root to root", "Jaw tips pushed down into the grooves until they seat on the roots: the minor diameter."),
):
    body = f'<path d="{rod_v(cx, 60, 50, 118)}" {PART}/>'
    body += jaws_down(xa, xb, 10, 96)
    body += ext_v(xa, 96, 138) + ext_v(xb, 96, 138)
    body += hdim(xa, xb, 138, sid.lower(), label, ty=154)
    body += f'<text x="{cx+62}" y="40" {TXTM}>insert, axis</text><text x="{cx+62}" y="53" {TXTM}>vertical</text>'
    F[sid] = fig(sid.lower(), 320, 162, body, cap)

# ---------- A3 pitch ----------
body = f'<path d="{rod_v(cx, 60, 30, 118)}" {PART}/>'
ys = (36, 48, 60, 72, 84)
body += tips_right(ys, 52, cx-36+6, 20, 104)
for i, y in enumerate(ys):
    body += f'<circle cx="{cx-36}" cy="{y}" r="2.4" {REDF}/>'
    body += f'<text x="{cx+42}" y="{y+4}" {TXTM}>crest {i+1}</text>'
body += vdim(38, 36, 84, "a3", "span", side=-1)
body += f'<text x="16" y="140" {TXTR}>pitch = span ÷ (5 − 1)</text>'
body += f'<text x="16" y="155" {TXTM}>count inclusive · repeat from the other end</text>'
F["A3"] = fig("a3", 320, 162, body, "Tips on the first and last crest you can reach; pitch is the span divided by the number of crests minus one.")

# ---------- A4 starts ----------
def end_view(cx, cy, r, starts, l1, l2):
    b = f'<circle cx="{cx}" cy="{cy}" r="{r}" {PART}/><circle cx="{cx}" cy="{cy}" r="{r-9}" {PART2}/>'
    for k in range(starts):
        a = 2 * math.pi * k / starts - math.pi / 2
        x1, y1 = cx + (r-9) * math.cos(a), cy + (r-9) * math.sin(a)
        x2, y2 = cx + (r+2) * math.cos(a), cy + (r+2) * math.sin(a)
        b += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {RED}/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="3" {REDF}/>'
    b += f'<text x="{cx}" y="{cy+r+16}" text-anchor="middle" {TXT}>{l1}</text>'
    b += f'<text x="{cx}" y="{cy+r+30}" text-anchor="middle" {TXTR}>{l2}</text>'
    return b
body = end_view(62, 56, 36, 1, "1 ridge begins", "1 start")
body += end_view(168, 56, 36, 2, "2 ridges begin", "2 starts")
body += f'<text x="236" y="30" {TXT}>or: one full turn,</text><text x="236" y="44" {TXT}>then measure the rise</text>'
body += f'<path d="M262 82 a15 15 0 1 1 -11 -14" {RED} marker-end="url(#a4a)"/>'
body += vdim(300, 62, 100, "a4", "rise", side=-1)
body += f'<text x="236" y="126" {TXTR}>starts = rise ÷ pitch</text>'
F["A4"] = fig("a4", 390, 140, body, "Looking at the tip of the thread: count how many separate ridges begin at the end face. One full turn advances one lead, and lead ÷ pitch gives the same number.")

# ---------- A5 length ----------
body = f'<rect x="80" y="20" width="120" height="26" rx="2" {PART}/>'
body += f'<path d="{rod_v(140, 56, 46, 140)}" {PART}/>'
body += ext_h(200, 46, 262) + ext_h(168, 140, 262)
body += depth_v(228, 46, 140, base_w=40)
body += vdim(258, 46, 140, "a5", "length", side=1)
body += f'<text x="14" y="36" {TXT}>flange</text><text x="14" y="100" {TXT}>thread</text>'
body += f'<text x="14" y="158" {TXTM}>enter measured − 0.5</text>'
F["A5"] = fig("a5", 320, 166, body, "Depth rod from the underside of the insert's flange to the tip of the thread.")

# ---------- A6 hand ----------
body = f'<circle cx="80" cy="62" r="44" {PART}/><circle cx="80" cy="62" r="34" {PART2}/>'
body += f'<path d="M52 36 a38 38 0 1 1 -6 20" {RED} marker-end="url(#a6a)"/>'
body += f'<text x="80" y="126" text-anchor="middle" {TXTM}>viewed from outside</text>'
body += f'<text x="150" y="44" {TXTR}>clockwise tightens</text><text x="150" y="60" {TXT}>= right-hand</text>'
body += f'<text x="150" y="88" {TXTM}>counter-clockwise tightens</text><text x="150" y="102" {TXTM}>= left-hand (rare)</text>'
F["A6"] = fig("a6", 320, 136, body, "Look at the thread you are screwing into; the direction that tightens names the hand.")

# ---------- A7 rim ----------
def neck(x, y, ID=44, wall=16, h=56):
    return (f'<rect x="{x}" y="{y}" width="{wall}" height="{h}" {PART}/>'
            f'<rect x="{x+wall+ID}" y="{y}" width="{wall}" height="{h}" {PART}/>')
body = neck(40, 40)
body += f'<rect x="50" y="116" width="56" height="8" rx="1" {CAL}/>'
body += f'<polygon points="56,116 62,116 58.5,48 56,48" {CAL}/><polygon points="100,116 94,116 97.5,48 100,48" {CAL}/>'
body += hdim(56, 100, 28, "a7", "rim ID · inside jaws", ty=18)
body += neck(190, 40)
body += jaws_down(190, 266, 4, 50)
body += ext_v(190, 96, 112) + ext_v(266, 96, 112)
body += hdim(190, 266, 112, "a7", "rim OD · outside jaws", ty=128)
body += f'<rect x="190" y="40" width="16" height="4" {REDF}/><rect x="250" y="40" width="16" height="4" {REDF}/>'
body += f'<text x="228" y="146" text-anchor="middle" {TXTM}>land = (OD − ID) ÷ 2 · needs &gt; 2 mm</text>'
F["A7"] = fig("a7", 320, 154, body, "Neck in section, insert removed. Inside jaws span the opening (ID); outside jaws span the neck at its top face (OD). The O-ring lands on the flat between them.")

# ---------- A8 flange OD + rim → ink ----------
body = f'<rect x="30" y="30" width="110" height="22" rx="2" {PART}/>'
body += jaws_down(30, 140, 4, 52)
body += ext_v(30, 52, 72) + ext_v(140, 52, 72)
body += hdim(30, 140, 72, "a8", "flange OD", ty=88)
body += f'<text x="85" y="104" text-anchor="middle" {TXTM}>hex may grow to this</text>'
body += f'<path d="M190 40 L190 130 L290 130 L290 40 L282 40 L282 122 L198 122 L198 40 Z" {PART2}/>'
body += f'<rect x="198" y="92" width="84" height="30" style="fill:var(--accent);opacity:.35"/>'
body += depth_v(224, 40, 92, base_w=36)
body += vdim(300, 40, 92, "a8", "", side=1)
body += f'<text x="306" y="36" text-anchor="end" {TXTR}>rim → ink</text>'
body += f'<text x="240" y="148" text-anchor="middle" {TXTM}>bottle about half full</text>'
F["A8"] = fig("a8", 320, 156, body, "Left: the insert's flange across the outside jaws. Right: depth rod from the neck rim down to the ink surface with the bottle half full.")

# ---------- B1 / B2 ----------
for sid, ra, label, cap in (
    ("B1", 23, "B1 · major, across crests", "Section held sideways under the caliper; jaw tips on the top and bottom crests of the short thread band."),
    ("B2", 18, "B2 · minor, tips in the grooves", "Same hold; tips pushed into opposite grooves until they seat on the roots."),
):
    body, k = section_h(60, 70)
    xm = (k["th0"] + k["th1"]) / 2
    body += jaws_right(k["cy"]-ra, k["cy"]+ra, 200, xm)  # beam to the right of the nib? no: nib is right; put beam left of body
    body = ""  # rebuild: beam on the left would collide with the body, so hang jaws from above instead
    body, k = section_h(40, 96)
    body += jaws_down(xm - 60 + 0, xm - 60 + 0, 0, 0) if False else ""
    # jaws from above: they need to reach the top and bottom crest — a caliper across a horizontal shaft
    # is drawn with its beam behind the part; show the beam as a vertical bar right of the band and two jaws.
    xm = (k["th0"] + k["th1"]) / 2
    body += f'<rect x="{k["nib1"]+30}" y="{k["cy"]-ra-30}" width="9" height="{2*ra+60}" rx="1" {CAL}/>'
    for y, s in ((k["cy"]-ra, -1), (k["cy"]+ra, +1)):
        body += f'<rect x="{xm+8}" y="{y if s>0 else y-7}" width="{k["nib1"]+30-xm-8}" height="7" {CAL}/>'
        body += f'<polygon points="{xm+8},{y} {xm+8},{y+s*7} {xm-6},{y+s*2.5} {xm-6},{y}" {CAL}/>'
    xd = k["nib1"] + 12
    body += ext_h(xm-6, k["cy"]-ra, xd+6) + ext_h(xm-6, k["cy"]+ra, xd+6)
    body += vdim(xd, k["cy"]-ra, k["cy"]+ra, sid.lower(), "", side=1)
    body += f'<text x="16" y="{k["cy"]+ra+34}" {TXTR}>{label}</text>'
    body += f'<text x="{k["body0"]+6}" y="{k["cy"]-40}" {TXTM}>section</text><text x="{k["th1"]+8}" y="{k["cy"]+36}" {TXTM}>nib</text>'
    F[sid] = fig(sid.lower(), 320, 176, body, cap)

# ---------- B3 pitch ----------
body, k = section_h(40, 100)
xs = (k["th0"]+6, k["th0"]+18, k["th0"]+30, k["th0"]+42)
body += tips_down(xs, 10, k["cy"]-k["r_th"]-5, xs[0]-20, xs[-1]+20)
for x in xs:
    body += f'<circle cx="{x}" cy="{k["cy"]-k["r_th"]-5}" r="2.4" {REDF}/>'
body += ext_v(xs[0], k["cy"]+k["r_th"], k["cy"]+44) + ext_v(xs[-1], k["cy"]+k["r_th"], k["cy"]+44)
body += hdim(xs[0], xs[-1], k["cy"]+44, "b3", "span, 4 crests", ty=k["cy"]+60)
body += f'<text x="{k["nib1"]+10}" y="{k["cy"]-8}" {TXTR}>pitch = span ÷ 3</text>'
body += f'<text x="{k["nib1"]+10}" y="{k["cy"]+8}" {TXTM}>short band:</text><text x="{k["nib1"]+10}" y="{k["cy"]+22}" {TXTM}>do both ends</text>'
F["B3"] = fig("b3", 340, 172, body, "Tips on the first and last crest of the short band; with four crests the pitch is the span divided by three.")

# ---------- B4 starts via cap ----------
body = f'<rect x="40" y="30" width="60" height="96" rx="4" {PART}/><rect x="46" y="108" width="48" height="36" rx="3" {PART2}/>'
body += f'<line x1="70" y1="30" x2="70" y2="46" {RED}/><line x1="70" y1="108" x2="70" y2="122" {RED}/>'
body += f'<text x="70" y="160" text-anchor="middle" {TXTM}>marks aligned</text>'
body += f'<rect x="150" y="30" width="60" height="96" rx="4" {PART}/><rect x="156" y="108" width="48" height="36" rx="3" {PART2}/>'
body += f'<line x1="180" y1="30" x2="180" y2="46" {RED}/><line x1="180" y1="108" x2="180" y2="122" {RED}/>'
body += f'<path d="M192 20 a16 9 0 1 1 -24 0" {RED} marker-end="url(#b4a)"/>'
body += f'<text x="180" y="160" text-anchor="middle" {TXTM}>one full turn</text>'
body += vdim(226, 108, 128, "b4", "travel", side=1)
body += f'<text x="234" y="50" {TXT}>cap advances</text><text x="234" y="64" {TXT}>one lead per turn</text>'
body += f'<text x="234" y="92" {TXTR}>starts =</text><text x="234" y="106" {TXTR}>travel ÷ pitch</text>'
F["B4"] = fig("b4", 370, 170, body, "Pencil-mark cap and section, turn the cap exactly one turn, measure how far it moved along the axis. That travel is the lead.")

# ---------- B5 band length ----------
body, k = section_h(40, 70)
xl = k["th0"] + 42   # last crest
body += ext_v(k["sh1"], k["cy"]+36, k["cy"]+70) + ext_v(xl, k["cy"]+k["r_th"]+5, k["cy"]+70)
body += depth_h(k["cy"]+52, k["sh1"], xl, base_h=30)
body += hdim(k["sh1"], xl, k["cy"]+70, "b5", "B5 · band, shoulder to last crest", ty=k["cy"]+86, anchor="start", tx=k["sh1"]-20)
body += f'<text x="{k["sh0"]-8}" y="{k["cy"]-44}" text-anchor="end" {TXTM}>shoulder face</text>'
body += f'<line x1="{k["sh0"]-6}" y1="{k["cy"]-40}" x2="{k["sh1"]}" y2="{k["cy"]-36}" {MUT}/>'
F["B5"] = fig("b5", 320, 164, body, "Depth-rod base against the shoulder face, rod along the thread to the last crest: the length of the threaded band.")

# ---------- B6 shoulder land ----------
body, k = section_h(40, 74)
body += ext_h(k["sh0"], k["cy"]-36, 22) + ext_h(k["sh0"], k["cy"]+36, 22)
body += vdim(28, k["cy"]-36, k["cy"]+36, "b6", "", side=1)
body += f'<text x="16" y="{k["cy"]+58}" {TXTR}>shoulder OD</text>'
xe = k["th1"] + 22
body += ext_h(k["th1"], k["cy"]-23, xe+10) + ext_h(k["th1"], k["cy"]+23, xe+10)
body += vdim(xe+4, k["cy"]-23, k["cy"]+23, "b6", "", side=1)
body += f'<text x="{xe-24}" y="{k["cy"]+44}" {TXTR}>thread-end dia</text>'
body += f'<rect x="{k["sh1"]-3}" y="{k["cy"]-36}" width="3" height="13" {REDF}/><rect x="{k["sh1"]-3}" y="{k["cy"]+23}" width="3" height="13" {REDF}/>'
body += f'<text x="{k["sh1"]+4}" y="{k["cy"]-44}" {TXTM}>land · must be flat</text>'
F["B6"] = fig("b6", 320, 150, body, "The shoulder's outside diameter and the diameter where the thread meets it; the flat ring between (red) is what compresses the top O-ring.")

# ---------- B7 nib front view ----------
body = f'<path d="M132 74 L168 74 L168 130 L132 130 Z" {PART2}/>'
body += f'<line x1="140" y1="112" x2="160" y2="112" {MUT}/><line x1="140" y1="120" x2="160" y2="120" {MUT}/>'
body += f'<path d="M150 20 L184 70 L176 110 L150 118 L124 110 L116 70 Z" {PART}/>'
body += f'<line x1="150" y1="34" x2="150" y2="112" {MUT}/>'
body += jaws_down(116, 184, 4, 62)
body += ext_v(116, 70, 142) + ext_v(184, 70, 142)
body += hdim(116, 184, 142, "b7", "widest point + 1.0 = BORE_DIA", ty=158)
body += f'<text x="200" y="96" {TXTM}>check the feed too;</text><text x="200" y="110" {TXTM}>fins can be wider</text>'
F["B7"] = fig("b7", 320, 166, body, "Nib and feed seen from the front: the widest point across the nib shoulders, or across the feed if that is wider.")

# ---------- B8 reach ----------
body, k = section_h(20, 50)
body += ext_v(k["sh1"], k["cy"]+36, k["cy"]+62) + ext_v(k["nib1"], k["cy"]+3, k["cy"]+62)
body += hdim(k["sh1"], k["nib1"], k["cy"]+62, "b8", "shoulder → nib tip", ty=k["cy"]+78)
x0, y0 = 232, 20
body += f'<rect x="{x0}" y="{y0}" width="80" height="14" {PART}/>'
body += f'<path d="M{x0} {y0+14} L{x0} {y0+120} L{x0+80} {y0+120} L{x0+80} {y0+14}" {PART2}/>'
body += f'<rect x="{x0+1}" y="{y0+72}" width="78" height="47" style="fill:var(--accent);opacity:.35"/>'
body += f'<line x1="{x0+40}" y1="{y0+14}" x2="{x0+40}" y2="{y0+98}" {RED}/><path d="M{x0+35} {y0+98} L{x0+45} {y0+98} L{x0+40} {y0+106} Z" {REDF}/>'
body += f'<text x="{x0+86}" y="{y0+12}" {TXTM}>hex + tube</text>'
body += f'<text x="{x0+86}" y="{y0+50}" {TXTM}>rim → ink</text>'
body += f'<text x="{x0+86}" y="{y0+96}" {TXTR}>≥ 3 below</text>'
F["B8"] = fig("b8", 400, 160, body, "Left: shoulder to nib tip. Right: the adapter lifts the pen by hex plus tube, so the nib must still reach past the rim-to-ink distance by a few millimetres.")

# ---------- splice ----------
src = "/mnt/c/Users/brona/AppData/Local/Temp/claude/C--Users-brona/398b5ca9-5191-4149-bc9e-4505bb14e5d3/scratchpad/bench-guide.html"
html = open(src, encoding="utf-8").read()
html = re.sub(r'<figure class="fig">.*?</figure>\n\s*', '', html, flags=re.S)
css = ('.fig{margin:0 0 14px;max-width:540px}'
       '.fig svg{display:block;width:100%;height:auto;background:var(--surface);border:1px solid var(--rule-soft);color:var(--ink)}'
       '.fig figcaption{font-size:.82rem;color:var(--muted);margin-top:6px;line-height:1.4}\n')
if ".fig{" not in html:
    html = html.replace("/* checks */", css + "/* checks */", 1)
n = 0
for sid, figure in F.items():
    m = re.search(rf'<div class="id">{sid}<small>', html)
    assert m, sid
    k = html.index('<div class="bench">', m.end())
    html = html[:k] + figure + "\n      " + html[k:]
    n += 1
open(src, "w", encoding="utf-8", newline="\n").write(html)
print("inserted", n, "figures;", len(html), "bytes; figures in file:", html.count('class="fig"'))

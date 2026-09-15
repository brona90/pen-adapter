#!/usr/bin/env python3
"""
pen_adapter.py — parametric thread adapter, Asvine vacuum filler -> TWSBI Vac 20A bottle.

Bottom to top (Z up, Z=0 at the tip of the male thread):
    male thread   copies the external thread of TWSBI's grey knurled insert
    hex flange    grip; O-ring groove on its UNDERSIDE lands on the bottle neck rim
    female tube   the Asvine section screws in (same thread its cap uses);
                  O-ring groove on the TOP annular face, compressed by the section shoulder
    through bore  full length, clears nib + feed

Sealing is by the two O-ring face seals only. The threads locate, they do not seal.

Threads come from bd_warehouse (IsoThread / TrapezoidalThread), never a hand-swept profile.

Usage:
    uv run pen_adapter.py adapter            # the real part
    uv run pen_adapter.py male-gauge         # coupon: screws into the bottle
    uv run pen_adapter.py female-gauge       # coupon: the pen screws into it
    uv run pen_adapter.py all
    uv run pen_adapter.py adapter --clearance 0.2 --out out/
Every export is followed by a manifold check of the STL that was actually written.
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path

# ============================================================================
#  PARAMETERS — every dimension lives here.  All millimetres.
#
#  Anything tagged  MEASURE_ME  is a PLACEHOLDER: a plausible number so the
#  model builds, NOT a measurement.  Replace it before printing the real part
#  (README.md says how to measure each one with calipers).  Print the two
#  gauges first and tune RADIAL_CLEARANCE on them.
# ============================================================================

# ---- print-fit tuning -------------------------------------------------------
RADIAL_CLEARANCE = 0.15   # per-side radial offset applied to BOTH threads:
                          # the male thread shrinks by it, the female grows by it.
                          # 0.10-0.25 is the usual FDM range; tune on the gauges.

# ---- bottle side: male thread, copy of the grey insert's external thread ----
BOTTLE_THREAD_MAJOR_DIA = 12.0    # MEASURE_ME  crest-to-crest OD of the insert's thread
BOTTLE_THREAD_PITCH     = 1.0     # MEASURE_ME  crest-to-adjacent-crest distance
BOTTLE_THREAD_STARTS    = 1       # MEASURE_ME  1 unless the insert is multi-start
BOTTLE_THREAD_PROFILE   = "iso"   # "iso" = 60 deg V, single start only; "trap" = arbitrary
                                  # flank angle + multi-start (use for starts > 1)
BOTTLE_THREAD_ANGLE     = 60      # included flank angle, "trap" profile only
BOTTLE_THREAD_LENGTH    = 5.0     # MEASURE_ME  threaded length of the insert, tip to flange
BOTTLE_RIM_SEAL_DIA     = 14.0    # MEASURE_ME  mean diameter of the neck rim the O-ring lands on
                                  #             = (rim ID + rim OD) / 2

# ---- hex flange -------------------------------------------------------------
HEX_ACROSS_FLATS = 17.0           # grip; must also enclose the underside groove (checked)
HEX_THICKNESS    = 4.0

# ---- pen side: female thread, the Asvine section's cap thread ---------------
PEN_THREAD_MAJOR_DIA  = 12.0      # MEASURE_ME  crest-to-crest OD of the section thread
PEN_THREAD_PITCH      = 1.0       # MEASURE_ME  crest-to-adjacent-crest distance
PEN_THREAD_STARTS     = 1         # MEASURE_ME  pen threads are often 2- or 3-start; see README
PEN_THREAD_PROFILE    = "iso"     # as above
PEN_THREAD_ANGLE      = 60
PEN_THREAD_LENGTH     = 4.0       # MEASURE_ME  length of the threaded band on the section
PEN_THREAD_RELIEF     = 1.0       # unthreaded bore below the thread so the section's last
                                  # thread never bottoms out before the shoulder seats
PEN_SHOULDER_SEAL_DIA = 15.0      # MEASURE_ME  mean diameter of the section shoulder land
                                  #             that will press the top O-ring
TUBE_OD               = 18.0      # outer diameter of the female tube (wall is checked)
TUBE_HEIGHT           = 8.0       # tube above the hex flange

# ---- through bore -----------------------------------------------------------
BORE_DIA = 8.5                    # MEASURE_ME  widest point of nib + feed, plus ~1 mm

# ---- O-ring cord, face-seal grooves -----------------------------------------
ORING_CORD_DIA     = 1.0          # silicone cord cross-section
GROOVE_DEPTH_RATIO = 0.75         # groove depth / cord dia  -> 25 % squeeze
GROOVE_WIDTH_RATIO = 1.35         # groove width / cord dia  -> ~78 % gland fill

# ---- misc -------------------------------------------------------------------
HAND                = "right"     # both threads
MIN_WALL            = 0.8         # thinnest wall the checks will accept
THREAD_INTERFERENCE = 0.2         # bd_warehouse: how far the thread root sinks into the
                                  # core / wall so the boolean fuse is solid. Leave it.
MESH_TOLERANCE      = 0.01        # STL linear deflection
MESH_ANGULAR_TOL    = 0.1         # STL angular deflection (rad)

# ============================================================================
#  End of parameters.
# ============================================================================

from build123d import (  # noqa: E402
    Align, Axis, Cylinder, ExportSVG, Keep, LineType, Plane, Polygon, Pos,
    RegularPolygon, export_stl, extrude, revolve, section, split,
)
from bd_warehouse.thread import IsoThread, TrapezoidalThread  # noqa: E402

BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)
EPS = 0.05  # cutters poke this far past the face they open onto (avoids coplanar booleans)


@dataclass(frozen=True)
class ThreadSpec:
    name: str
    major_dia: float
    pitch: float
    starts: int
    profile: str
    angle: float

    def make(self, *, external: bool, length: float, clearance: float, end_finishes):
        """Build the bd_warehouse thread solid, clearance applied radially per side."""
        dia = self.major_dia + (-2 if external else 2) * clearance
        if self.profile == "iso":
            if self.starts != 1:
                raise ValueError(
                    f"{self.name}: IsoThread is single-start only; "
                    f"set {self.name.upper()}_THREAD_PROFILE = 'trap' for {self.starts} starts")
            return IsoThread(major_diameter=dia, pitch=self.pitch, length=length,
                             external=external, hand=HAND, end_finishes=end_finishes,
                             interference=THREAD_INTERFERENCE)
        if self.profile == "trap":
            return TrapezoidalThread(diameter=dia, pitch=self.pitch, thread_angle=self.angle,
                                     length=length, external=external, starts=self.starts,
                                     hand=HAND, end_finishes=end_finishes,
                                     interference=THREAD_INTERFERENCE)
        raise ValueError(f"{self.name}: profile must be 'iso' or 'trap', not {self.profile!r}")


BOTTLE = ThreadSpec("bottle", BOTTLE_THREAD_MAJOR_DIA, BOTTLE_THREAD_PITCH,
                    BOTTLE_THREAD_STARTS, BOTTLE_THREAD_PROFILE, BOTTLE_THREAD_ANGLE)
PEN = ThreadSpec("pen", PEN_THREAD_MAJOR_DIA, PEN_THREAD_PITCH,
                 PEN_THREAD_STARTS, PEN_THREAD_PROFILE, PEN_THREAD_ANGLE)

GROOVE_W = ORING_CORD_DIA * GROOVE_WIDTH_RATIO
GROOVE_D = ORING_CORD_DIA * GROOVE_DEPTH_RATIO


# ----------------------------------------------------------------------------
#  Derived geometry + sanity checks
# ----------------------------------------------------------------------------
@dataclass
class Layout:
    clearance: float
    male: object
    female: object
    z_flange_bottom: float
    z_flange_top: float
    z_top: float
    male_root_r: float
    female_root_r: float   # radius of the bore the internal thread lives in (= major/2 + clr)
    female_apex_r: float
    cone_h: float
    z_thread_bottom: float
    z_relief_bottom: float
    z_cone_bottom: float


def layout(clearance: float) -> Layout:
    male = BOTTLE.make(external=True, length=BOTTLE_THREAD_LENGTH, clearance=clearance,
                       end_finishes=("fade", "square"))       # fade at the tip, square into flange
    female = PEN.make(external=False, length=PEN_THREAD_LENGTH, clearance=clearance,
                      end_finishes=("square", "fade"))        # square at the bottom, fade at entry
    z_fb = BOTTLE_THREAD_LENGTH
    z_ft = z_fb + HEX_THICKNESS
    z_top = z_ft + TUBE_HEIGHT
    fr = female.root_radius
    cone_h = fr - BORE_DIA / 2                                # 45 deg cone, self-supporting
    z_tb = z_top - PEN_THREAD_LENGTH
    z_rb = z_tb - PEN_THREAD_RELIEF
    z_cb = z_rb - cone_h
    L = Layout(clearance, male, female, z_fb, z_ft, z_top, male.root_radius, fr,
               female.apex_radius, cone_h, z_tb, z_rb, z_cb)
    check(L)
    return L


def check(L: Layout) -> None:
    """Fail loudly, naming the parameter to change, before any geometry is built."""
    problems = []
    hex_flat_r = HEX_ACROSS_FLATS / 2
    tube_r = TUBE_OD / 2
    bore_r = BORE_DIA / 2
    male_major_r = BOTTLE_THREAD_MAJOR_DIA / 2

    # male section wall: core minus thread interference minus bore
    w = L.male_root_r - THREAD_INTERFERENCE - bore_r
    if w < MIN_WALL:
        problems.append(f"male thread wall {w:.2f} < MIN_WALL {MIN_WALL}: "
                        f"reduce BORE_DIA or the bottle thread is too small for this bore")
    # underside groove must clear the male thread and stay inside the hex flats
    g_in = BOTTLE_RIM_SEAL_DIA / 2 - GROOVE_W / 2
    g_out = BOTTLE_RIM_SEAL_DIA / 2 + GROOVE_W / 2
    if g_in - male_major_r < 0.3:
        problems.append(f"underside groove inner radius {g_in:.2f} is within 0.3 of the male "
                        f"thread crest {male_major_r:.2f}: raise BOTTLE_RIM_SEAL_DIA")
    if hex_flat_r - g_out < MIN_WALL:
        problems.append(f"underside groove outer radius {g_out:.2f} leaves {hex_flat_r - g_out:.2f} "
                        f"to the hex flat: raise HEX_ACROSS_FLATS to >= "
                        f"{2 * (g_out + MIN_WALL):.1f}")
    if GROOVE_D >= HEX_THICKNESS - MIN_WALL:
        problems.append("HEX_THICKNESS too thin for the underside groove")
    # top groove must clear the female thread wall and stay inside the tube
    t_in = PEN_SHOULDER_SEAL_DIA / 2 - GROOVE_W / 2
    t_out = PEN_SHOULDER_SEAL_DIA / 2 + GROOVE_W / 2
    if t_in - (L.female_root_r + THREAD_INTERFERENCE) < 0.3:
        problems.append(f"top groove inner radius {t_in:.2f} is within 0.3 of the female thread "
                        f"root {L.female_root_r + THREAD_INTERFERENCE:.2f}: raise PEN_SHOULDER_SEAL_DIA")
    if tube_r - t_out < MIN_WALL:
        problems.append(f"top groove outer radius {t_out:.2f} leaves {tube_r - t_out:.2f} to the "
                        f"tube OD: raise TUBE_OD to >= {2 * (t_out + MIN_WALL):.1f}")
    # tube wall around the female thread
    w = tube_r - L.female_root_r - THREAD_INTERFERENCE
    if w < MIN_WALL:
        problems.append(f"tube wall {w:.2f} < MIN_WALL: raise TUBE_OD")
    # the void profile must not dip into the male thread section
    if L.z_cone_bottom < L.z_flange_bottom:
        problems.append(f"female bore + relief + cone reach z={L.z_cone_bottom:.2f}, below the "
                        f"flange underside z={L.z_flange_bottom:.2f}: raise TUBE_HEIGHT or "
                        f"HEX_THICKNESS, or shorten PEN_THREAD_LENGTH/PEN_THREAD_RELIEF")
    if L.cone_h <= 0:
        problems.append("BORE_DIA is not smaller than the female thread bore; nothing to step down to")
    if problems:
        sys.exit("PARAMETER CHECK FAILED:\n  - " + "\n  - ".join(problems))


def report(L: Layout) -> None:
    print(f"clearance {L.clearance} mm/side")
    print(f"  male  thread: major {BOTTLE_THREAD_MAJOR_DIA - 2*L.clearance:.2f}  "
          f"root r {L.male_root_r:.2f}  wall to bore {L.male_root_r - THREAD_INTERFERENCE - BORE_DIA/2:.2f}")
    print(f"  female thread: bore r {L.female_root_r:.2f}  crest r {L.female_apex_r:.2f}  "
          f"tube wall {TUBE_OD/2 - L.female_root_r - THREAD_INTERFERENCE:.2f}")
    print(f"  grooves: {GROOVE_W:.2f} wide x {GROOVE_D:.2f} deep for {ORING_CORD_DIA} cord")
    print(f"  cord cut lengths: bottom {math.pi*BOTTLE_RIM_SEAL_DIA:.1f} mm, "
          f"top {math.pi*PEN_SHOULDER_SEAL_DIA:.1f} mm")
    print(f"  z: flange {L.z_flange_bottom:.2f}..{L.z_flange_top:.2f}, top face {L.z_top:.2f}, "
          f"female thread {L.z_thread_bottom:.2f}..{L.z_top:.2f}, cone {L.z_cone_bottom:.2f}..{L.z_relief_bottom:.2f}")
    hex_corner = HEX_ACROSS_FLATS / math.cos(math.radians(30))
    if TUBE_OD > HEX_ACROSS_FLATS:
        print(f"  note: TUBE_OD {TUBE_OD} > hex flats {HEX_ACROSS_FLATS} "
              f"(hex corners {hex_corner:.1f}); grip is fine, just looks top-heavy")


# ----------------------------------------------------------------------------
#  Geometry pieces
# ----------------------------------------------------------------------------
def hex_prism(height: float):
    circ_r = HEX_ACROSS_FLATS / math.sqrt(3)     # across-flats -> circumradius
    return extrude(RegularPolygon(radius=circ_r, side_count=6), amount=height)


def face_groove(mean_dia: float, z_face: float, *, opens_downward: bool):
    """Annular cutter for an O-ring face-seal groove, poking EPS out of the face."""
    ri, ro = mean_dia / 2 - GROOVE_W / 2, mean_dia / 2 + GROOVE_W / 2
    h = GROOVE_D + EPS
    ring = Cylinder(ro, h, align=BOTTOM) - Cylinder(ri, h, align=BOTTOM)
    z0 = z_face - EPS if opens_downward else z_face - GROOVE_D
    return Pos(0, 0, z0) * ring


def pen_void(L: Layout, z_bottom: float):
    """One revolved cutter: through bore -> 45 deg cone -> relief -> female thread bore -> out the top.
    (r, z) profile in Plane.XZ local coords (x = radius, y = Z)."""
    br, fr = BORE_DIA / 2, L.female_root_r
    pts = [
        (0, z_bottom - EPS),
        (br, z_bottom - EPS),
        (br, L.z_cone_bottom),
        (fr, L.z_relief_bottom),          # cone
        (fr, L.z_top + EPS),              # relief + thread bore
        (0, L.z_top + EPS),
    ]
    return revolve(Plane.XZ * Polygon(*pts, align=None), axis=Axis.Z)


def male_stack(L: Layout):
    """Male thread on its core + hex flange with the underside groove (no bore yet)."""
    body = Cylinder(L.male_root_r, BOTTLE_THREAD_LENGTH, align=BOTTOM)
    body += Pos(0, 0, L.z_flange_bottom) * hex_prism(HEX_THICKNESS)
    body -= face_groove(BOTTLE_RIM_SEAL_DIA, L.z_flange_bottom, opens_downward=True)
    body += L.male
    return body


def female_stack(L: Layout, z_bottom: float, height: float):
    """Tube from z_bottom with the female thread, the void, and the top groove."""
    body = Pos(0, 0, z_bottom) * Cylinder(TUBE_OD / 2, height, align=BOTTOM)
    body -= pen_void(L, z_bottom)
    body -= face_groove(PEN_SHOULDER_SEAL_DIA, L.z_top, opens_downward=False)
    body += Pos(0, 0, L.z_thread_bottom) * L.female
    return body


# ----------------------------------------------------------------------------
#  Parts
# ----------------------------------------------------------------------------
def build_adapter(L: Layout):
    body = male_stack(L)
    body += Pos(0, 0, L.z_flange_top) * Cylinder(TUBE_OD / 2, TUBE_HEIGHT, align=BOTTOM)
    body -= pen_void(L, -1.0)
    body -= face_groove(PEN_SHOULDER_SEAL_DIA, L.z_top, opens_downward=False)
    body += Pos(0, 0, L.z_thread_bottom) * L.female
    return body.clean()


def build_male_gauge(L: Layout):
    """Male thread + hex flange + groove + bore. Screws into the bottle; nothing above the hex."""
    body = male_stack(L)
    body -= Pos(0, 0, -1) * Cylinder(BORE_DIA / 2, L.z_flange_top + 2, align=BOTTOM)
    return body.clean()


def build_female_gauge(L: Layout):
    """Just the tube: female thread, relief, cone, bore, top groove. The pen screws into it.
    Sits with its flat base one wall below the cone bottom."""
    z_bottom = L.z_cone_bottom - MIN_WALL
    return female_stack(L, z_bottom, L.z_top - z_bottom).clean()


PARTS = {
    "adapter": build_adapter,
    "male-gauge": build_male_gauge,
    "female-gauge": build_female_gauge,
}


# ----------------------------------------------------------------------------
#  Verification — read the geometry, do not assume it
# ----------------------------------------------------------------------------
def verify_brep(part, name: str) -> float:
    solids = part.solids()
    if len(solids) != 1:
        sys.exit(f"{name}: expected 1 solid, got {len(solids)} - booleans did not fuse")
    valid = part.is_valid() if callable(part.is_valid) else part.is_valid
    if not valid:
        sys.exit(f"{name}: BRepCheck reports an INVALID shape")
    shells = solids[0].shells()
    from OCP.BRep import BRep_Tool
    closed = [BRep_Tool.IsClosed_s(s.wrapped) for s in shells]
    if len(shells) != 1 or not all(closed):
        sys.exit(f"{name}: solid has {len(shells)} shells, closed={closed}; expected one closed shell")
    vol = part.volume
    if vol <= 0:
        sys.exit(f"{name}: non-positive volume {vol}")
    print(f"  BRep: 1 solid, 1 closed shell, valid, volume {vol:.1f} mm^3, "
          f"{len(part.faces())} faces")
    return vol


def verify_stl(path: Path, name: str, brep_volume: float) -> None:
    import trimesh
    # STL carries no vertex sharing (3 fresh vertices per triangle), so coincident
    # vertices must be merged before edge adjacency means anything - exactly what a
    # slicer does on import. Any edge still owned by != 2 triangles is a real hole.
    m = trimesh.load(path, force="mesh", process=True)
    m.merge_vertices()
    bad = []
    if not m.is_watertight:
        bad.append("not watertight (open edges)")
    if not m.is_winding_consistent:
        bad.append("inconsistent winding")
    if not m.is_volume:
        bad.append("not a valid volume (normals inconsistent / negative volume)")
    # every part here is a ring (through bore): a genus-1 closed surface has Euler number 0
    if m.euler_number != 0:
        bad.append(f"Euler number {m.euler_number}, expected 0 for a single genus-1 body")
    if abs(m.volume - brep_volume) / brep_volume > 0.02:
        bad.append(f"mesh volume {m.volume:.1f} differs from BRep {brep_volume:.1f} by >2%")
    if bad:
        sys.exit(f"{name}: STL FAILED manifold check: " + "; ".join(bad))
    print(f"  STL:  watertight, consistent winding, Euler {m.euler_number}, "
          f"{len(m.faces)} triangles, volume {m.volume:.1f} mm^3")


# ----------------------------------------------------------------------------
#  Section views
# ----------------------------------------------------------------------------
def export_section(part, name: str, out: Path) -> list[Path]:
    written = []
    # (a) half the solid, cut on the XZ plane - load next to the full STL in a slicer/viewer
    half = split(part, bisect_by=Plane.XZ, keep=Keep.BOTTOM)
    p = out / f"{name}-half.stl"
    export_stl(half, str(p), tolerance=MESH_TOLERANCE, angular_tolerance=MESH_ANGULAR_TOL)
    written.append(p)

    # (b) the cross-section face itself, filled, as PNG - the internal thread profile is
    #     the saw-tooth on the inside of the tube wall
    sec = section(part, section_by=Plane.XZ)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 8), dpi=150)
    for face in sec.faces():
        verts, tris = face.tessellate(0.02)
        xs = [v.X for v in verts]
        zs = [v.Z for v in verts]
        ax.tripcolor(xs, zs, tris, facecolors=[1.0] * len(tris), cmap="Greys",
                     vmin=0, vmax=1.6, edgecolors="none")
        for wire in face.wires():
            pts = [wire.position_at(i / 800) for i in range(801)]
            ax.plot([q.X for q in pts], [q.Z for q in pts], color="black", lw=0.6)
    ax.set_aspect("equal")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Z (mm)")
    ax.set_title(f"{name} - section on XZ plane (clearance {RADIAL_CLEARANCE})")
    ax.grid(True, lw=0.3, alpha=0.5)
    p = out / f"{name}-section.png"
    fig.savefig(p, bbox_inches="tight")
    plt.close(fig)
    written.append(p)

    # (c) SVG line drawing of the half part, viewed from -Y
    visible, hidden = half.project_to_viewport((0, -200, 0), viewport_up=(0, 0, 1))
    svg = ExportSVG(scale=8)
    svg.add_layer("visible")
    svg.add_layer("hidden", line_color=(128, 128, 128), line_type=LineType.ISO_DASH)
    svg.add_shape(visible, layer="visible")
    svg.add_shape(hidden, layer="hidden")
    p = out / f"{name}-half.svg"
    svg.write(str(p))
    written.append(p)
    return written


# ----------------------------------------------------------------------------
#  CLI
# ----------------------------------------------------------------------------
def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", choices=[*PARTS, "all"])
    ap.add_argument("--out", type=Path, default=Path("out"))
    ap.add_argument("--clearance", type=float, default=RADIAL_CLEARANCE,
                    help="override RADIAL_CLEARANCE (mm per side)")
    ap.add_argument("--no-section", action="store_true", help="skip the section-view exports")
    args = ap.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)
    L = layout(args.clearance)
    report(L)

    names = list(PARTS) if args.part == "all" else [args.part]
    for name in names:
        print(f"\n== {name}")
        part = PARTS[name](L)
        vol = verify_brep(part, name)
        stl = args.out / f"{name}.stl"
        export_stl(part, str(stl), tolerance=MESH_TOLERANCE, angular_tolerance=MESH_ANGULAR_TOL)
        verify_stl(stl, name, vol)
        print(f"  wrote {stl}")
        if not args.no_section:
            for p in export_section(part, name, args.out):
                print(f"  wrote {p}")


if __name__ == "__main__":
    main()

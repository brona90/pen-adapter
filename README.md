# pen-adapter

Parametric, 3D-printable thread adapter that lets an **Asvine vacuum-filling
fountain pen** screw into a **TWSBI Vac 20A** ink bottle, replacing TWSBI's grey
knurled insert. Modelled in [build123d](https://build123d.readthedocs.io/) on the
OpenCASCADE kernel; threads come from `bd_warehouse.thread` (`IsoThread` /
`TrapezoidalThread`), not a hand-swept helix.

```
        ┌──────────┐   top face: O-ring groove, pen shoulder lands here
        │ ╲      ╱ │   female thread (Asvine section / cap thread)
        │  ╲    ╱  │   relief, then 45° cone down to the bore
   ┌────┴─────────┴────┐
   │      hex flange   │   underside: O-ring groove, sits on the bottle neck rim
   └────┬─────────┬────┘
        │╱╲╱╲╱╲╱╲╱│   male thread (copy of the grey insert's external thread)
        └────┬────┘
        through bore, full length, clears nib + feed
```

Sealing is by the two O-ring **face seals**; the threads only locate. Printed
threads at this pitch will not hold a vacuum, so nothing depends on them sealing.

**Every dimension marked `MEASURE_ME` in `pen_adapter.py` is a placeholder.**
The numbers there are plausible enough for the model to build and be checked;
they are not measurements. Measure first (below), then print the two gauges,
then the part.

## Reproducing the build

Environment recorded in `pyproject.toml`, `uv.lock`, `.python-version`:

| what | value |
|---|---|
| host | WSL2 Debian (this was built on `warealien`) |
| uv | 0.11.2 |
| python | uv-managed CPython 3.13.12 (`python-preference = "only-managed"`) |
| build123d | 0.11.1 |
| bd_warehouse | 0.3.0 |
| cadquery-ocp | 7.8.x manylinux wheel (pulled in by build123d) |
| checks | trimesh 5.1.0, matplotlib 3.11 (section PNG) |

```sh
cd ~/keep/pen-adapter
uv sync                       # installs the pinned interpreter + locked deps
uv run pen_adapter.py all     # builds, verifies and exports everything into out/
```

Why not a Nix shell: nixpkgs has no `build123d`/`cadquery-ocp`, and the
Nix-profile Python (3.14, Nix glibc) cannot `dlopen` Debian's
`/lib/x86_64-linux-gnu/libstdc++.so.6`, which the manylinux OCP wheel needs —
`import OCP` fails with `libstdc++.so.6: cannot open shared object file`. The
`only-managed` setting stops uv from ever picking that interpreter up. The wheel
also needs the Debian packages `libstdc++6`, `libgl1`, `libx11-6` (already
present here).

## CLI

```
uv run pen_adapter.py {adapter|male-gauge|female-gauge|all} [--out DIR]
                      [--clearance MM] [--no-section]
```

For each part it writes to `out/` (git-ignored, regenerable):

| file | what |
|---|---|
| `<part>.stl` | the printable solid |
| `<part>-half.stl` | the solid cut on the XZ plane — load next to the full STL to look inside |
| `<part>-section.png` | filled cross-section on the XZ plane; the **internal thread** is the saw-tooth on the inside of the tube wall between the top face and the relief |
| `<part>-half.svg` | line drawing of the half part, visible + hidden edges |

Nothing is written until the parameter check passes, and every STL is checked
after it is written (see *Verification*). A failing check exits non-zero and
names the parameter to change.

### Parts

- **`adapter`** — the real thing.
- **`male-gauge`** — the male thread + hex flange + underside groove + bore,
  nothing above the hex. Screw it into the bottle. Tests the bottle thread fit
  and whether the underside groove lands on the neck rim.
- **`female-gauge`** — just the tube: female thread, relief, cone, bore, top
  groove, flat base. Screw the pen into it. Tests the pen thread fit and whether
  the top groove lands under the section shoulder.

## Measurements you need to take

Vernier/digital calipers only, no pitch gauge. Zero the calipers first, use light
pressure on plastic, and measure each diameter at three angular positions and
take the largest (threads are rarely perfectly round, and jaws slip into
grooves).

### 1. Pitch, without a pitch gauge

Put one jaw tip on the crest of the first thread and the other on the crest of
the last thread you can reach, parallel to the axis. Count the **crests** you
spanned, `N`. Then

    pitch = distance / (N - 1)

Span as many threads as you can; over five crests a 0.05 mm caliper error is
only ~0.01 mm on the pitch. Do it twice. If the jaws will not sit on crests,
press the thread firmly into a strip of Blu-Tack or a wax/soap block and measure
the imprint the same way.

### 2. Starts (multi-start threads)

Pen cap threads are very often 2- or 3-start; bottle inserts are usually
single. Two checks:

- **Look at the end of the thread.** Count how many separate ridges begin at the
  end face. That is the number of starts.
- **Measure the lead.** Mark the pen and cap with a pencil, screw the cap
  *exactly one full turn*, measure how far it advanced with the depth rod. That
  advance is the lead; `starts = lead / pitch`. A 1.0 mm crest-to-crest thread
  that advances 2.0 mm per turn is 2-start.

`IsoThread` is single-start only. For `starts > 1` set the profile to `"trap"`
and give the flank angle (60 if it looks like an ordinary V; 30 if the crests
are wide and flat).

### 3. Major diameter (both threads are external — measure the real parts)

- **TWSBI insert:** outside jaws across the thread crests, perpendicular to the
  axis → `BOTTLE_THREAD_MAJOR_DIA`.
- **Asvine section:** outside jaws across the section's thread crests →
  `PEN_THREAD_MAJOR_DIA`.

Also take the **minor** diameter (jaw tips down in opposite grooves). You do not
enter it, but `(major - minor) / 2` is the tooth depth: for a 60° V it is about
`0.54 × pitch`. If your thread is much shallower than that it is a truncated or
rounded form; the modelled thread is then deeper than the real one, which is
harmless on the female side and means the male side may want +0.05 mm
clearance.

### 4. Thread lengths

- **Insert:** depth rod from the underside of the insert's flange to the tip →
  `BOTTLE_THREAD_LENGTH`. Use ~0.5 mm *less* than measured so the flange O-ring
  seats before the thread bottoms in the neck.
- **Section:** length of the threaded band on the section, from the shoulder to
  the last crest → `PEN_THREAD_LENGTH`. `PEN_THREAD_RELIEF` (1.0 mm default)
  adds unthreaded bore below it so the section's last thread never hits the
  cone before the shoulder meets the O-ring.

### 5. Seal landing diameters

- **Bottle neck rim** (where the flange underside lands): inside jaws for the
  rim ID, outside jaws for the rim OD.
  `BOTTLE_RIM_SEAL_DIA = (ID + OD) / 2`. The rim's flat land, `(OD - ID) / 2`,
  must be wider than the groove (1.35 mm) with margin either side — if it is
  under ~2 mm, tell me, the groove ratios need to change.
- **Section shoulder** (the step the cap seats against): outside diameter of the
  shoulder, and the diameter where the thread ends against it.
  `PEN_SHOULDER_SEAL_DIA` = their mean. Same land-width caveat.

### 6. Bore

Widest point of nib + feed together (usually across the nib shoulders) →
`BORE_DIA = that + 1.0`.

### 7. Hand

Almost certainly right-hand for both. Confirm: looking into the bottle neck /
the cap, tightening clockwise means right-hand.

## Print, then tune

Print orientation: **top face on the bed, male thread pointing up.** The male
thread then prints with no overhangs, the female thread's 60° flanks are
self-supporting, the cone under the female thread is 45° so it needs no support,
and the hex only overhangs the tube by the corners (< 1 mm). Set the slicer's
elephant-foot compensation (≈ 0.15 mm) so the top-face groove edges stay sharp.
Layer height 0.1–0.12 mm for a 1 mm pitch; 0.4 nozzle is fine. PETG or ABS
rather than PLA if you want it to live in an ink bottle. If you have a resin
printer, use it — thread detail is far better, and start at
`--clearance 0.08`.

1. `uv run pen_adapter.py male-gauge` and try it in the bottle. Won't start or
   binds → `--clearance 0.20`; sloppy → `--clearance 0.10`. Repeat.
2. `uv run pen_adapter.py female-gauge`, same with the pen.
3. Set `RADIAL_CLEARANCE` in the file to the value that fit (both threads share
   one clearance; if they want different values, split the constant — it is used
   in exactly one place, `ThreadSpec.make`).
4. `uv run pen_adapter.py adapter`.

## O-rings

Both grooves are sized for **1.0 mm silicone cord**: 1.35 mm wide × 0.75 mm
deep, i.e. 25 % squeeze and ~78 % gland fill. The script prints the cord cut
lengths for the two grooves (`π × mean diameter`). Cut square, join with a drop
of cyanoacrylate; or buy 1.0 mm cross-section O-rings with an ID just under the
groove mean diameter. Different cord: change `ORING_CORD_DIA` only.

## Verification (what "done" means here)

For every exported part the script checks, in order, and stops on the first
failure:

1. **Parameter check** — walls ≥ `MIN_WALL`, grooves clear the threads and stay
   inside the hex/tube, the void does not reach into the male thread section.
2. **BRep** — exactly one solid, `BRepCheck` valid, exactly one shell and it is
   closed, positive volume.
3. **STL as written** — reloaded with trimesh, coincident vertices merged (STL
   has no vertex sharing; this is what a slicer does): watertight (every edge
   owned by exactly two triangles), consistent winding, a valid volume, Euler
   number 0 (one closed genus-1 surface — the part is a ring because of the
   bore), and mesh volume within 2 % of the BRep volume.

The gate was mutation-tested: an STL with ten triangles removed, one with
flipped winding, and one scaled by 2 % were each rejected with the expected
message. The 2-start trapezoidal path was also built and passed the same checks.

## Layout of `pen_adapter.py`

- **Parameters** — the top of the file, all of them, all in mm.
- `ThreadSpec.make` — the only place the thread classes are called; clearance is
  applied there, radially, per side (male shrinks, female grows).
- `layout()` / `check()` — derived Z positions and the parameter check.
- `pen_void()` — the whole internal profile (bore → cone → relief → thread
  bore) is one revolved cutter, so there are no coplanar cylinder-on-cylinder
  booleans.
- `build_*` — the three parts, composed from `male_stack` / `female_stack`.
- `verify_brep` / `verify_stl` / `export_section`.

bd_warehouse builds each thread as a compound of helical loop solids whose root
sinks `THREAD_INTERFERENCE` (0.2 mm) into the core or wall; that overlap is what
makes the boolean fuse produce one solid. Leave it alone.

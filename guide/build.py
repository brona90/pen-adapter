#!/usr/bin/env python3
"""
guide/build.py — assemble the bench-guide site from the model, the figures and the template.

    uv run pen_adapter.py all      # first: builds, gates and exports every part into out/
    uv run guide/build.py          # then: writes site/index.html and copies out/ into site/out/

What goes into the page and where it comes from:
    hero section outline    the adapter model, cut on the XZ plane (build123d `section`)
    16 step figures         guide/figures.py, hand-drawn inline SVG
    check constants         pen_adapter.py — the page enforces the same numbers the script does
    build stamp             git revision + UTC date; status = how many MEASURE_ME tags remain
    downloads               out/report.json — only what passed the manifold gate is listed
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "guide"))

import pen_adapter as pa  # noqa: E402
from figures import F  # noqa: E402
from build123d import Plane, section  # noqa: E402

OUT = ROOT / "out"
SITE = ROOT / "site"
TEMPLATE = ROOT / "guide" / "template.html"
REPO_URL = "https://github.com/brona90/pen-adapter"
PART_LABEL = {"adapter": "adapter", "male-gauge": "male gauge", "female-gauge": "female gauge"}


def section_paths() -> list[str]:
    """Two closed SVG paths: the adapter's section on the centre plane, in mm, y = -Z."""
    layout = pa.layout(pa.RADIAL_CLEARANCE)
    part = pa.build_adapter(layout)
    sec = section(part, section_by=Plane.XZ)
    paths = []
    for face in sec.faces():
        for wire in face.wires():
            pts, last = [], None
            for i in range(700):
                p = wire.position_at(i / 700)
                q = (round(p.X, 2), round(-p.Z, 2))
                if q != last:
                    pts.append(q)
                    last = q
            paths.append("M" + " L".join(f"{x} {y}" for x, y in pts) + " Z")
    if len(paths) != 2:
        sys.exit(f"expected 2 section outlines (left and right half), got {len(paths)}")
    return paths


def revision() -> str:
    sha = os.environ.get("GITHUB_SHA")
    if not sha:
        try:
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        except Exception:
            sha = "local"
    return sha[:7]


def downloads(report: dict) -> str:
    rows = []
    for name in ("adapter", "male-gauge", "female-gauge"):
        r = report.get(name)
        if not r:
            continue
        links = " ".join(f'<a href="out/{f}">{f}</a>' for f in r["files"])
        rows.append(f'<tr><td class="n">{PART_LABEL[name]}</td>'
                    f'<td class="g">✓ 1 closed solid · watertight · Euler {r["euler"]}<br>'
                    f'{r["brep_volume"]} mm³ B-rep · {r["mesh_volume"]} mm³ mesh · {r["triangles"]} triangles</td>'
                    f'<td class="f">{links}</td></tr>')
    meta = report.get("_meta", {})
    return ('<div class="dl"><div class="bar"><span>built by the pipeline from this revision · every file below passed the gate'
            f' · clearance {meta.get("clearance", pa.RADIAL_CLEARANCE)}</span>'
            f'<span>{"placeholder geometry" if meta.get("measure_me_left") else "measured geometry"}</span></div>'
            '<table><thead><tr><th>part</th><th>gate</th><th>files</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>")


def main() -> None:
    report_path = OUT / "report.json"
    if not report_path.exists():
        sys.exit("out/report.json missing — run `uv run pen_adapter.py all` first")
    report = json.loads(report_path.read_text())
    measure_me_left = report.get("_meta", {}).get("measure_me_left", 0)

    html = TEMPLATE.read_text(encoding="utf-8")
    p0, p1 = section_paths()
    subs = {
        "__PATH0__": p0, "__PATH1__": p1,
        "__GW__": f"{pa.GROOVE_W:.2f}", "__MINWALL__": str(pa.MIN_WALL), "__INTERF__": str(pa.THREAD_INTERFERENCE),
        "__CLR__": str(pa.RADIAL_CLEARANCE), "__HEX__": str(pa.HEX_ACROSS_FLATS), "__TUBE__": str(pa.TUBE_OD),
        "__H_ABOVE__": str(pa.HEX_THICKNESS + pa.TUBE_HEIGHT),
        "__REV__": revision(), "__DATE__": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "__STATUS__": (f"placeholder geometry · {measure_me_left} MEASURE_ME left" if measure_me_left else "measured geometry"),
        "__DOWNLOADS__": downloads(report),
        "__FOOTER__": (f'built from <a href="{REPO_URL}">brona90/pen-adapter</a> @ {revision()} · pen_adapter.py · '
                       "readings are kept in this browser, and on claude.ai also in the page's store as <code>measurements/current</code>"),
    }
    for sid, figure in F.items():
        subs[f"__FIG_{sid}__"] = figure
    for k, v in subs.items():
        if k not in html:
            sys.exit(f"template has no {k}")
        html = html.replace(k, v)
    left = sorted(set(re.findall(r"__[A-Z0-9_]+__", html)))
    if left:
        sys.exit(f"unfilled placeholders: {left}")

    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "out").mkdir(parents=True)
    (SITE / "index.html").write_text(html, encoding="utf-8", newline="\n")
    (SITE / ".nojekyll").write_text("")
    copied = 0
    for f in OUT.iterdir():
        if f.suffix in (".stl", ".step", ".png", ".svg", ".json"):
            shutil.copy2(f, SITE / "out" / f.name)
            copied += 1
    print(f"wrote {SITE / 'index.html'} ({len(html)} bytes, {len(F)} figures, rev {revision()}), {copied} files into site/out/")


if __name__ == "__main__":
    main()

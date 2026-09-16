# guide/

Source of the bench guide. The page is **built**, not edited: the section drawing comes
from the model, the constants in the fit checks come from `pen_adapter.py`, and the
downloads table lists only files that passed the manifold gate.

| file | role |
|---|---|
| `template.html` | the page with `__PLACEHOLDERS__` — edit this for copy, layout, style |
| `figures.py` | the 16 step figures, hand-drawn inline SVG; `F` maps step id → `<figure>` |
| `build.py` | fills the template: section outline from the model, figures, constants, build stamp, downloads; writes `site/` |

```sh
uv run pen_adapter.py all    # out/: STL, STEP, half-STL, section PNG/SVG, report.json
uv run guide/build.py        # site/index.html + site/out/
```

`site/` is git-ignored; `.github/workflows/build.yml` runs the same two commands on every
push to `main` and deploys `site/` to GitHub Pages. The published page saves worksheet
readings in the browser; the same HTML published as a claude.ai Artifact also saves them
to the artifact's store (`claude.use("db")`), and it detects which host it is on.

Placeholders `build.py` fills: `__PATH0__ __PATH1__` (section halves), `__FIG_A1__ … __FIG_B8__`,
`__GW__ __MINWALL__ __INTERF__ __CLR__ __HEX__ __TUBE__ __H_ABOVE__` (check constants),
`__REV__ __DATE__ __STATUS__` (title block / stamp), `__DOWNLOADS__`, `__FOOTER__`.
A placeholder the template lacks, or one left unfilled, fails the build.

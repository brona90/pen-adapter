import re
p = "/mnt/c/Users/brona/AppData/Local/Temp/claude/C--Users-brona/398b5ca9-5191-4149-bc9e-4505bb14e5d3/scratchpad/bench-guide.html"
s = open(p, encoding="utf-8").read()

def rep(a, b, count=1):
    global s
    assert a in s, "MISSING: " + a[:70]
    s = s.replace(a, b, count)

# ---------- tokens: the blueprint plate is a committed single-theme island ----------
rep("  color-scheme:light;\n}", "  color-scheme:light;\n  --bp:#0F2A5E; --bp-line:#E8F0FF; --bp-fill:rgba(232,240,255,.16); --bp-call:#9CC0FF; --bp-mark:#F5B84B;\n  --bp-grid:rgba(232,240,255,.075); --bp-grid5:rgba(232,240,255,.16); --bp-edge:rgba(232,240,255,.28);\n}")

# ---------- hero plate ----------
rep(".drawing{background:var(--surface);border:1px solid var(--rule);box-shadow:var(--shadow);padding:18px 18px 10px;overflow-x:auto}",
    ".drawing{background:var(--bp);color:var(--bp-line);border:1px solid var(--bp-edge);box-shadow:var(--shadow);overflow-x:auto}\n"
    ".drawing .plate{padding:14px 14px 6px}")
rep(".drawing svg{display:block;width:100%;height:auto;min-width:760px;font-family:var(--mono)}",
    ".drawing svg{display:block;width:100%;height:auto;min-width:760px;font-family:var(--mono);border:1px solid var(--bp-edge);"
    "background-image:linear-gradient(var(--bp-grid5) 1px,transparent 1px),linear-gradient(90deg,var(--bp-grid5) 1px,transparent 1px),"
    "linear-gradient(var(--bp-grid) 1px,transparent 1px),linear-gradient(90deg,var(--bp-grid) 1px,transparent 1px);"
    "background-size:calc(500%/60) calc(500%/22),calc(500%/60) calc(500%/22),calc(100%/60) calc(100%/22),calc(100%/60) calc(100%/22)}")
rep(".drawing .cap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:.8rem;color:var(--muted);padding-top:8px;font-family:var(--mono)}",
    ".tblock{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));border-top:1px solid var(--bp-edge);font-family:var(--mono)}\n"
    ".tblock div{padding:8px 12px;border-right:1px solid var(--bp-edge);display:flex;flex-direction:column;gap:2px;min-width:0}\n"
    ".tblock div:last-child{border-right:0}\n"
    ".tblock span{font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;color:var(--bp-call)}\n"
    ".tblock b{font-size:.8rem;font-weight:600;color:var(--bp-line);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n"
    ".tblock b.mark{color:var(--bp-mark)}")
rep(".section-fill{fill:var(--accent-soft);stroke:var(--ink);stroke-width:.12}", ".section-fill{fill:var(--bp-fill);stroke:var(--bp-line);stroke-width:.14}")
rep(".callout{stroke:var(--accent);stroke-width:.1;fill:none}", ".callout{stroke:var(--bp-call);stroke-width:.1;fill:none}")
rep(".callout-dot{fill:var(--accent)}", ".callout-dot{fill:var(--bp-call)}")
rep(".lbl{font-size:.72px;fill:var(--ink)}", ".lbl{font-size:.72px;fill:var(--bp-line)}\n.lbl a{cursor:pointer}.lbl a:hover .m,.lbl a:focus .m{text-decoration:underline}")
rep(".lbl .p{fill:var(--accent);font-weight:600}", ".lbl .p{fill:#fff;font-weight:600}")
rep(".lbl .m{fill:var(--warn)}", ".lbl .m{fill:var(--bp-mark);font-weight:600}")
rep(".dim{stroke:var(--muted);stroke-width:.08;fill:none}", ".dim{stroke:var(--bp-call);stroke-width:.08;fill:none}")
rep(".dimtxt{font-size:.62px;fill:var(--muted)}", ".dimtxt{font-size:.62px;fill:var(--bp-call)}\n"
    "@media (prefers-reduced-motion: no-preference){\n"
    "  .section-fill.draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.4s cubic-bezier(.4,0,.2,1) .15s forwards}\n"
    "  .arrive{opacity:0;transform:translateY(.4px);animation:arrive .5s ease forwards}\n"
    "  .arrive:nth-of-type(1){animation-delay:.7s}.arrive:nth-of-type(2){animation-delay:.95s}.arrive:nth-of-type(3){animation-delay:1.2s}\n"
    "  .hero h1{animation:rise .7s ease both}.hero .deck{animation:rise .7s ease .15s both}\n"
    "}\n"
    "@keyframes draw{to{stroke-dashoffset:0}}@keyframes arrive{to{opacity:1;transform:none}}@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}")

# ---------- figures become plates too ----------
rep(".fig svg{display:block;width:100%;height:auto;background:var(--surface);border:1px solid var(--rule-soft);color:var(--ink)}",
    ".fig svg{display:block;width:100%;height:auto;color:var(--bp-line);background-color:var(--bp);border:1px solid var(--bp-edge);"
    "background-image:radial-gradient(var(--bp-grid5) .9px,transparent 1px);background-size:16px 16px;"
    "--accent-soft:var(--bp-fill);--surface-2:rgba(232,240,255,.07);--warn:var(--bp-mark);--muted:var(--bp-call);--surface:transparent}")

# ---------- steps: done state, rail counts, ring, units, stamp ----------
rep(".step .id{font-family:var(--display);font-size:2.2rem;font-weight:800;line-height:.9;color:var(--accent)}",
    ".step .id{font-family:var(--display);font-size:2.2rem;font-weight:800;line-height:.9;color:var(--accent);transition:color .3s}\n"
    ".step.done .id{color:var(--ok)}.step.done .id small{color:var(--ok)}.step.done .id small::before{content:\"✓ \"}\n"
    ".step.done .bench{border-color:var(--ok)}.step.done .result .v{color:var(--ok)}")
rep(".rail nav a{display:grid;grid-template-columns:32px 1fr;", ".rail nav a{display:grid;grid-template-columns:32px 1fr auto;")
rep(".rail nav a .n{font-family:var(--mono);font-size:.72rem;color:var(--muted)}",
    ".rail nav a .n{font-family:var(--mono);font-size:.72rem;color:var(--muted)}\n"
    ".rail nav a .c{font-family:var(--mono);font-size:.7rem;color:var(--muted);font-variant-numeric:tabular-nums}.rail nav a .c.ok{color:var(--ok)}\n"
    ".ringbox{display:grid;grid-template-columns:44px 1fr;gap:10px;align-items:center;margin-bottom:8px}\n"
    ".ring{width:44px;height:44px;transform:rotate(-90deg)}.ring circle{fill:none;stroke-width:4}.ring .bg{stroke:var(--rule-soft)}.ring .fg{stroke:var(--accent);transition:stroke-dasharray .4s ease}\n"
    ".ringbox b{font-family:var(--display);font-size:1.6rem;font-weight:800;line-height:1;color:var(--ink)}.ringbox small{display:block;font-family:var(--mono);font-size:.66rem;letter-spacing:.06em;color:var(--muted)}")
rep(".result .v{font-family:var(--display);font-size:2.6rem;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}",
    ".result .v{font-family:var(--display);font-size:2.6rem;font-weight:800;line-height:1;font-variant-numeric:tabular-nums;transition:color .3s}\n"
    ".result .v .u{font-family:var(--mono);font-size:.78rem;font-weight:400;color:var(--muted);margin-left:5px}\n"
    ".stamp{display:inline-block;border:2px solid var(--warn);color:var(--warn);font-family:var(--mono);font-size:.64rem;letter-spacing:.14em;padding:2px 7px;transform:rotate(-2deg);margin-left:12px;vertical-align:middle}")

# ---------- markup: rail counts + ring ----------
rep('<a href="#bottle"><span class="n">03</span><span>Bottle side</span></a>', '<a href="#bottle"><span class="n">03</span><span>Bottle side</span><span class="c" id="c_bottle"></span></a>')
rep('<a href="#pen"><span class="n">04</span><span>Pen side</span></a>', '<a href="#pen"><span class="n">04</span><span>Pen side</span><span class="c" id="c_pen"></span></a>')
rep('<a href="#params"><span class="n">06</span><span>Parameter block</span></a>', '<a href="#params"><span class="n">06</span><span>Parameter block</span><span class="c" id="c_params"></span></a>')
rep('  <div class="savebox">\n    <b>Worksheet</b>',
    '  <div class="savebox">\n    <div class="ringbox"><svg class="ring" viewBox="0 0 36 36" aria-hidden="true"><circle class="bg" cx="18" cy="18" r="15.5"/><circle class="fg" id="ringfg" cx="18" cy="18" r="15.5" pathLength="100" stroke-dasharray="0 100" stroke-linecap="round"/></svg>'
    '<div><b id="ringtxt">0 / 14</b><small>parameters measured</small></div></div>\n    <b>Worksheet</b>')

# ---------- markup: hero stamp, plate wrapper, title block ----------
rep('<div class="eyebrow">Asvine vacuum filler × TWSBI Vac 20A · replacing the grey insert</div>',
    '<div class="eyebrow">Asvine vacuum filler × TWSBI Vac 20A · replacing the grey insert <span class="stamp">REV A · 2026-09-16</span></div>')
rep('<div class="drawing">\n  <svg viewBox="-30 -19.8 60 21.8"', '<div class="drawing">\n <div class="plate">\n  <svg viewBox="-30 -20 60 22"')
rep('<path class="section-fill" d="M7.67', '<path class="section-fill draw" pathLength="1" d="M7.67')
rep('<path class="section-fill" d="M-9.81', '<path class="section-fill draw" pathLength="1" d="M-9.81')
# callout groups arrive in sequence: lines, dots, labels
s = s.replace('<g class="callout">', '<g class="callout arrive">').replace('<g class="callout-dot">', '<g class="callout-dot arrive">')
s = s.replace('<g class="lbl">', '<g class="lbl arrive">').replace('<g class="lbl" text-anchor="end">', '<g class="lbl arrive" text-anchor="end">')
# step letters link to their steps
s = re.sub(r'<tspan class="m">([AB]\d)</tspan>', lambda m: f'<a href="#{m.group(1).lower()}"><tspan class="m">{m.group(1)}</tspan></a>', s)
rep('  <div class="cap"><span>section on the XZ plane · from <code>out/adapter-section</code> · placeholder geometry, clearance 0.15</span><span>letters = the step that measures it</span></div>\n</div>',
    ' </div>\n  <div class="tblock">'
    '<div><span>Part</span><b>pen-adapter · adapter</b></div>'
    '<div><span>View</span><b>section A–A on XZ · from the model</b></div>'
    '<div><span>Units · grid</span><b>mm · 1 mm, heavy every 5</b></div>'
    '<div><span>Clearance</span><b>0.15 / side (default)</b></div>'
    '<div><span>Letters</span><b class="mark">the step that measures it</b></div>'
    '<div><span>Status</span><b class="mark">placeholder geometry</b></div>'
    '</div>\n</div>')

# ---------- step ids ----------
s = re.sub(r'<div class="step">(\s*<div class="id">)([AB]\d)<small>', lambda m: f'<div class="step" id="{m.group(2).lower()}">{m.group(1)}{m.group(2)}<small>', s)
assert s.count('<div class="step" id=') == 16, s.count('<div class="step" id=')

# ---------- JS: units, done states, counts, ring ----------
rep("  const set = (id, v, cls) => { const el = $('#'+id); if(!el) return; el.textContent = v === null ? '—' : v; el.classList.toggle('empty', v === null); if(cls!==undefined){ el.className = 'v' + (v===null?' empty':''); } };",
    "  const MM = new Set(['r_a1','r_a3','r_a5','r_a7','r_a8','r_b1','r_b3','r_b5','r_b6','r_b7','r_b8']);\n"
    "  const set = (id, v, cls) => { const el = $('#'+id); if(!el) return; el.textContent = v === null ? '—' : v; if(v !== null && MM.has(id)){ const u = document.createElement('span'); u.className = 'u'; u.textContent = 'mm'; el.appendChild(u); } el.classList.toggle('empty', v === null); };")
rep("    $('#paramcount').textContent = `${n} of 14 measured`;",
    "    $('#paramcount').textContent = `${n} of 14 measured`;\n"
    "    $('#ringfg').setAttribute('stroke-dasharray', `${n/14*100} 100`); $('#ringtxt').textContent = `${n} / 14`;\n"
    "    const cp = $('#c_params'); cp.textContent = `${n}/14`; cp.className = 'c' + (n===14?' ok':'');")
rep("  function render(){ const D = compute(); checks(D); code(D); }",
    "  function progress(){\n"
    "    document.querySelectorAll('.step').forEach(st => { const v = st.querySelector('.result .v'); st.classList.toggle('done', !!v && v.firstChild && v.firstChild.textContent.trim() !== '—'); });\n"
    "    for(const [sec, id] of [['#bottle','#c_bottle'],['#pen','#c_pen']]){ const all = document.querySelectorAll(sec+' .step'); const done = document.querySelectorAll(sec+' .step.done'); const el = $(id); el.textContent = `${done.length}/${all.length}`; el.className = 'c' + (done.length===all.length?' ok':''); }\n"
    "  }\n"
    "  function render(){ const D = compute(); checks(D); code(D); progress(); }")

open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(s))

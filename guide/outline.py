import sys, json
sys.path.insert(0, "/home/gfoster/keep/pen-adapter")
import pen_adapter as pa
from build123d import Plane, section
L = pa.layout(pa.RADIAL_CLEARANCE)
part = pa.build_adapter(L)
sec = section(part, section_by=Plane.XZ)
polys = []
for face in sec.faces():
    for wire in face.wires():
        n = 700
        pts = [wire.position_at(i / n) for i in range(n)]
        polys.append([[round(p.X, 3), round(p.Z, 3)] for p in pts])
json.dump({"polys": polys, "z": {"flange_bottom": L.z_flange_bottom, "flange_top": L.z_flange_top,
           "top": L.z_top, "thread_bottom": L.z_thread_bottom, "relief_bottom": L.z_relief_bottom,
           "cone_bottom": L.z_cone_bottom}}, open("/home/gfoster/.cache/claude-scratch/outline.json", "w"))
print(len(polys), "polygons;", sum(len(p) for p in polys), "points")

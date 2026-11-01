"""Parametric 3D-printable case for the 5 Volt Buck with UVLO board.

Board frame: X along the 40 mm length (Wago end at X=0, USB end at X=40),
Y across the 18 mm width, Z=0 at the PCB top surface. All sizes in mm.
Generated with FreeCAD 0.21 (freecadcmd). Edit the parameter block and re-run.
"""
import FreeCAD, Part, math, json, os
from FreeCAD import Vector as V, Matrix, Placement
# Run with:  freecadcmd -c "exec(open('case/make_case.py').read())"   (from the repo root)
# Outputs STEP/STL into the case/ folder. Set KICAD_3D_MODELS to the folder holding
# 292303-1.step and "Wago 2060-452.STEP" to enable the interference check; otherwise it is skipped.
OUT=os.path.join(os.getcwd(), "case"); os.makedirs(OUT, exist_ok=True)
SCR=OUT
L3D=os.environ.get("KICAD_3D_MODELS", "")

# ---------------- parameters (board frame: X 0..40 along length, Y 0..18 across, Z=0 = board top) ----------
BW, BL, BT, BR = 40.0, 18.0, 1.6, 2.5
CLR   = 0.4      # board edge to inner wall
EXT   = 10.0     # extra cavity length at the wire end: room for a zip tie on the cable as a pull stop
WALL  = 2.0
FLOOR = 2.6
STAND = 1.0      # floor top to board bottom (through-hole pins are trimmed flush)
ABOVE = 9.0      # board top to lid underside (USB top 7.9, inductor 7.1)
LID_T = 2.0
LIP_H, LIP_T, LIP_CLR = 2.5, 1.2, 0.2
HOLES = [(5.5,15.5),(5.5,2.5),(27.57,9.0)]      # board mounting holes, 3.0 mm
PILLAR_D, PILLAR_HOLE = 5.5, 2.7                # base pillars, M2.5 clearance
CB_D, CB_DEPTH = 5.2, 1.8                        # counterbore for pan-head in floor
BOSS_D, BOSS_HOLE, BOSS_DEPTH = 4.6, 2.0, 7.0    # lid bosses, M2.5 self-tap pilot
USB_Y, USB_Z, USB_CLR = (2.43,15.57), (1.30,7.05), 0.5
CABLE_D, CABLE_Z, CABLE_CSK = 7.0, 1.5, 9.0     # round cable entry: hole, centre height above board top, outside countersink
BTN_SLOTS = [(7.3,12.5,5.3,8.7),(7.3,12.5,9.3,12.7)]
VENT_X=[16.0,18.5,21.0,23.5]; VENT_W=1.2; VENT_Y=(3.5,14.5)

# derived
ix0, iy0, ix1, iy1 = -CLR-EXT, -CLR, BW+CLR, BL+CLR      # cavity incl. wire-end extension
ox0, oy0, ox1, oy1 = ix0-WALL, iy0-WALL, ix1+WALL, iy1+WALL
IR, OR_ = BR+CLR, BR+CLR+WALL
Z_FLOOR_BOT = -BT-STAND-FLOOR     # -7.2
Z_FLOOR_TOP = -BT-STAND           # -4.6
Z_WALL_TOP  = ABOVE               # 9.0
Z_LID_TOP   = ABOVE+LID_T         # 11.0

def rrect(x0,y0,x1,y1,r,z0,h):
    b=Part.makeBox(x1-x0,y1-y0,h,V(x0,y0,z0))
    ve=[e for e in b.Edges if abs(e.Vertexes[0].Point.x-e.Vertexes[1].Point.x)<1e-7 and abs(e.Vertexes[0].Point.y-e.Vertexes[1].Point.y)<1e-7]
    return b.makeFillet(r, ve)
def cyl(d,h,p,dirv=V(0,0,1)): return Part.makeCylinder(d/2,h,p,dirv)
def box(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))

# ---------------- base ----------------
base = rrect(ox0,oy0,ox1,oy1,OR_, Z_FLOOR_BOT, Z_WALL_TOP-Z_FLOOR_BOT)
base = base.cut(rrect(ix0,iy0,ix1,iy1,IR, Z_FLOOR_TOP, Z_WALL_TOP-Z_FLOOR_TOP+1))
for (hx,hy) in HOLES:
    base = base.fuse(cyl(PILLAR_D, STAND, V(hx,hy,Z_FLOOR_TOP)))
for (hx,hy) in HOLES:
    base = base.cut(cyl(PILLAR_HOLE, FLOOR+STAND+1, V(hx,hy,Z_FLOOR_BOT-0.5)))
    base = base.cut(cyl(CB_D, CB_DEPTH+0.5, V(hx,hy,Z_FLOOR_BOT-0.5)))
# USB: U-slot in the end wall, open to the top
uy0=USB_Y[0]-USB_CLR; uy1=USB_Y[1]+USB_CLR; uz0=USB_Z[0]-USB_CLR
base = base.cut(box(BW-1.0, ox1+2, uy0, uy1, uz0, Z_WALL_TOP+1))
# cable entry: one round hole in the end wall, countersunk on the outside
base = base.cut(cyl(CABLE_D, WALL+2, V(ox0-1, BL/2, CABLE_Z), V(1,0,0)))
base = base.cut(Part.makeCone(CABLE_CSK/2, CABLE_D/2, (CABLE_CSK-CABLE_D)/2, V(ox0-0.001, BL/2, CABLE_Z), V(1,0,0)))
# the 10 mm extension is free space: a zip tie cinched on the cable here is bigger than the
# entry hole, so a yank on the cable stops at the tie instead of at the Wago connection
# board end stops either side of the Wago, so the board cannot slide into the extension
for (y0,y1) in ((iy0, 3.6), (BL-3.6, iy1)):
    base = base.fuse(box(-CLR-1.0, -CLR, y0, y1, Z_FLOOR_TOP, 0.0))
# floor vents
for vx in VENT_X:
    base = base.cut(box(vx-VENT_W/2, vx+VENT_W/2, VENT_Y[0], VENT_Y[1], Z_FLOOR_BOT-1, Z_FLOOR_TOP+1))
# side-wall vents (long walls), small slots near the top
for sx in (16.0,18.5,21.0,23.5):
    base = base.cut(box(sx-VENT_W/2, sx+VENT_W/2, oy0-1, iy0+1, 3.0, 7.0))
    base = base.cut(box(sx-VENT_W/2, sx+VENT_W/2, iy1-1, oy1+1, 3.0, 7.0))
try:
    bot=[e for e in base.Edges if abs(e.BoundBox.ZMin-Z_FLOOR_BOT)<1e-6 and abs(e.BoundBox.ZMax-Z_FLOOR_BOT)<1e-6 and e.Length>3]
    base = base.makeChamfer(0.6, bot)
except Exception as ex: print("base chamfer skipped:", ex)

# ---------------- lid ----------------
lid = rrect(ox0,oy0,ox1,oy1,OR_, Z_WALL_TOP, LID_T)
lip = rrect(ix0+LIP_CLR, iy0+LIP_CLR, ix1-LIP_CLR, iy1-LIP_CLR, IR-LIP_CLR, Z_WALL_TOP-LIP_H, LIP_H)
lip = lip.cut(rrect(ix0+LIP_CLR+LIP_T, iy0+LIP_CLR+LIP_T, ix1-LIP_CLR-LIP_T, iy1-LIP_CLR-LIP_T, max(0.5,IR-LIP_CLR-LIP_T), Z_WALL_TOP-LIP_H-1, LIP_H+2))
lip = lip.cut(box(BW-4, ox1+1, uy0-0.5, uy1+0.5, Z_WALL_TOP-LIP_H-1, Z_WALL_TOP+1))   # clear USB shell
lid = lid.fuse(lip)
# tab filling the wall slot above the USB shell
tab = box(ix1-0.2, ox1, uy0+0.15, uy1-0.15, USB_Z[1]+USB_CLR, Z_WALL_TOP)
lid = lid.fuse(tab)
# bosses down to board top
for (hx,hy) in HOLES:
    lid = lid.fuse(cyl(BOSS_D, ABOVE, V(hx,hy,0)))
for (hx,hy) in HOLES:
    lid = lid.cut(cyl(BOSS_HOLE, BOSS_DEPTH, V(hx,hy,-0.001)))
# Wago push-button access slots and vents through the plate
for (x0,x1,y0,y1) in BTN_SLOTS:
    lid = lid.cut(box(x0,x1,y0,y1, Z_WALL_TOP-LIP_H-1, Z_LID_TOP+1))
for vx in VENT_X:
    lid = lid.cut(box(vx-VENT_W/2, vx+VENT_W/2, VENT_Y[0], VENT_Y[1], Z_WALL_TOP-1, Z_LID_TOP+1))
try:
    top=[e for e in lid.Edges if abs(e.BoundBox.ZMin-Z_LID_TOP)<1e-6 and abs(e.BoundBox.ZMax-Z_LID_TOP)<1e-6 and e.Length>3 and (abs(e.BoundBox.XMin-ox0)<1e-6 or abs(e.BoundBox.XMax-ox1)<1e-6 or abs(e.BoundBox.YMin-oy0)<1e-6 or abs(e.BoundBox.YMax-oy1)<1e-6)]
    lid = lid.makeChamfer(0.6, top)
except Exception as ex: print("lid chamfer skipped:", ex)

base = base.removeSplitter(); lid = lid.removeSplitter()
print("VALID base", base.isValid(), "lid", lid.isValid(), "solids", len(base.Solids), len(lid.Solids))
print("VOL base %.0f mm3  lid %.0f mm3" % (base.Volume, lid.Volume))
bb=base.BoundBox; print("BASE bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
bb=lid.BoundBox;  print("LID  bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))

# ---------------- board + component models for interference check ----------------
X0,Y0=140.265,63.255
def kx(fp, off, rot):
    px,py,prot=fp; rx,ry,rz=rot; m=Matrix()
    m.rotateX(math.radians(-rx)); m.rotateY(math.radians(-ry)); m.rotateZ(math.radians(-rz))
    m.move(V(*off)); m.rotateZ(math.radians(prot)); m.move(V(px-X0, Y0-py, 0)); return m
def load(path,fp,off,rot):
    sh=Part.Shape(); sh.read(path); sh.Placement=Placement(kx(fp,off,rot)); return sh
board = rrect(0,0,BW,BL,BR,-BT,BT)
for (hx,hy) in HOLES: board = board.cut(cyl(3.0, BT+2, V(hx,hy,-BT-1)))
comps = {
 "L1 7070 envelope": box(19.085-4.15,19.085+4.15,6.755-4.15,6.755+4.15,0,7.3),
 "board": board,
}
if L3D and os.path.exists(L3D+"/292303-1.step"):
    usb_full = load(L3D+"/292303-1.step",(172.1325,57.755,90.0),(3.5,-5.7,-2.8),(-90,0,0))
    # the through-hole pins are trimmed flush on the real board: keep at most 0.8 mm below the PCB for the check
    comps["USB J2 (pins trimmed)"] = usb_full.common(box(-20,60,-20,40,-BT-0.8,20))
    comps["Wago J1"] = load(L3D+"/Wago 2060-452.STEP",(148.265,54.255,0.0),(0,0,0),(-90,0,0))
else:
    print("KICAD_3D_MODELS not set: skipping connector interference check")
for name,sh in comps.items():
    for cname,c in (("base",base),("lid",lid)):
        try:
            v=c.common(sh).Volume
        except Exception as ex:
            v=float('nan'); print("  common failed", name, cname, ex)
        print(f"INTERFERENCE {name:18} vs {cname}: {v:.3f} mm3")

# ---------------- export ----------------
import Import, MeshPart, Mesh
doc=FreeCAD.newDocument("case")
def add(name,shape):
    o=doc.addObject("Part::Feature",name); o.Shape=shape; return o
# assembled (board frame, for viewing)
oA=[add("Case_Base",base), add("Case_Lid",lid), add("PCB_outline",board)]
doc.recompute()
Import.export(oA, OUT+"/usb-adapter-case-assembled.step")
# print orientation: base floor on Z=0; lid upside-down beside it
base_p = base.copy(); base_p.translate(V(0,0,-Z_FLOOR_BOT))
lid_p = lid.copy(); lid_p.rotate(V(0,0,0),V(1,0,0),180); lid_p.translate(V(0, oy1+ (oy1-oy0) + 10, Z_LID_TOP))  # mirrored in Y by the flip, then shifted
lb=lid_p.BoundBox; lid_p.translate(V(0, (oy0 + (oy1-oy0) + 10) - lb.YMin, -lb.ZMin))
oP=[add("Base_print",base_p), add("Lid_print",lid_p)]
doc.recompute()
Import.export(oP, OUT+"/usb-adapter-case.step")
for o,fn in ((oP[0],"usb-adapter-case-base.stl"),(oP[1],"usb-adapter-case-lid.stl")):
    m=MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.03, AngularDeflection=0.25, Relative=False)
    m.write(OUT+"/"+fn)
    print("STL", fn, "facets", m.CountFacets)
# triangle dump for preview rendering
def tris(shape):
    vs,fs=shape.tessellate(0.08)
    return {"v":[[p.x,p.y,p.z] for p in vs],"f":fs}
exploded_lid = lid.copy(); exploded_lid.translate(V(0,0,14))
prev={"base":tris(base),"lid":tris(exploded_lid),"board":tris(board),"ind":tris(comps["L1 7070 envelope"]),"lid_closed":tris(lid)}
if "USB J2 (pins trimmed)" in comps: prev["usb"]=tris(comps["USB J2 (pins trimmed)"]); prev["wago"]=tris(comps["Wago J1"])
if os.environ.get("PREVIEW_JSON"): json.dump(prev, open(os.environ["PREVIEW_JSON"],"w"))
json.dump({"outer_mm":[round(ox1-ox0,1),round(oy1-oy0,1),round(Z_LID_TOP-Z_FLOOR_BOT,1)],"wall":WALL,"floor":FLOOR,"lid":LID_T,
           "usb_protrusion_mm":round(44.88-ox1,1),"standoff":STAND,"wire_end_extension":EXT,"cable_hole_mm":CABLE_D,
           "screws":"3x M2.5 x 10 self-tapping, from below"}, open(OUT+"/case-dimensions.json","w"), indent=1)
print("DONE")

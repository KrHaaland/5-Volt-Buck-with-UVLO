"""Parametric 3D-printable case for the 5 Volt Buck with UVLO board.

Board frame: X along the 40 mm length (Wago end at X=0, USB end at X=40),
Y across the 18 mm width, Z=0 at the PCB top surface. All sizes in mm.
Generated with FreeCAD 0.21 (freecadcmd). Edit the parameter block and re-run.
"""
import FreeCAD, Part, math, json, os, re
from FreeCAD import Vector as V
# Run with:  freecadcmd -c "exec(open('case/make_case.py').read())"   (from the repo root)
# Outputs STEP/STL into the case/ folder. The populated board comes from USB-Adapter.step, the
# KiCad STEP export in the repo root, and every part of it is checked against the case.
OUT=os.path.join(os.getcwd(), "case"); os.makedirs(OUT, exist_ok=True)
PCB_STEP=os.path.join(os.getcwd(), "USB-Adapter.step")

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
CB_D, CB_DEPTH = 5.2, 2.1                        # counterbore in the floor; a 2.0 mm pan head sits 0.1 mm below the bottom face
BOSS_D, BOSS_HOLE, BOSS_DEPTH = 4.6, 2.0, 7.5    # lid bosses, M2.5 self-tap pilot
SCREW_D, SCREW_L, HEAD_D, HEAD_H = 2.5, 10.0, 5.0, 2.0   # M2.5 x 10 pan-head self-tapping screws (ISO 7045 size head)
USB_Y, USB_Z, USB_CLR = (2.43,15.57), (1.30,7.05), 0.5   # shell body section (Y, Z) and the gap around it in the wall slot
USB_FLANGE_X, USB_FLANGE_GAP = 44.55, 0.3   # the shell's front flange starts here; the end wall stops this far short of it
USB_TABS, TAB_CLR = (42.35, 42.50, 1.35, 16.65), 0.3   # side latch tabs on the shell (X range, Y reach): groove inside the wall
WAGO_Y, WAGO_TOP, BOSS_FLAT_CLR = (5.04,12.96), 4.66, 0.45   # the two bosses beside the Wago get a flat up to its top
CABLE_D, CABLE_Z, CABLE_CSK = 7.0, 1.5, 9.0     # round cable entry: hole, centre height above board top, outside countersink
BTN_SLOTS = [(7.3,12.5,5.3,8.7),(7.3,12.5,9.3,12.7)]

# derived
ix0, iy0, ix1, iy1 = -CLR-EXT, -CLR, BW+CLR, BL+CLR      # cavity incl. wire-end extension
ox0, oy0, ox1, oy1 = ix0-WALL, iy0-WALL, USB_FLANGE_X-USB_FLANGE_GAP, iy1+WALL   # USB end wall is thicker: it reaches the flange
IR, OR_ = BR+CLR, BR+CLR+WALL
Z_FLOOR_BOT = -BT-STAND-FLOOR     # -5.2
Z_FLOOR_TOP = -BT-STAND           # -2.6
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
# groove for the shell's side latch tabs, inside the wall and hidden under the lid
base = base.cut(box(USB_TABS[0]-TAB_CLR, USB_TABS[1]+TAB_CLR, USB_TABS[2]-TAB_CLR, USB_TABS[3]+TAB_CLR, uz0, Z_WALL_TOP+1))
# cable entry: one round hole in the end wall, countersunk on the outside
base = base.cut(cyl(CABLE_D, WALL+2, V(ox0-1, BL/2, CABLE_Z), V(1,0,0)))
base = base.cut(Part.makeCone(CABLE_CSK/2, CABLE_D/2, (CABLE_CSK-CABLE_D)/2, V(ox0-0.001, BL/2, CABLE_Z), V(1,0,0)))
# the 10 mm extension is free space: a zip tie cinched on the cable here is bigger than the
# entry hole, so a yank on the cable stops at the tie instead of at the Wago connection
# board end stops either side of the Wago, so the board cannot slide into the extension
for (y0,y1) in ((iy0, 3.6), (BL-3.6, iy1)):
    base = base.fuse(box(-CLR-1.0, -CLR, y0, y1, Z_FLOOR_TOP, 0.0))
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
    # the board holes beside the Wago leave only 1 mm between hole edge and connector body: flatten the
    # boss on that side, but only as high as the connector, so the threaded part above keeps a full wall
    if hy < WAGO_Y[0] and hy+BOSS_D/2 > WAGO_Y[0]-BOSS_FLAT_CLR:
        lid = lid.cut(box(hx-BOSS_D, hx+BOSS_D, WAGO_Y[0]-BOSS_FLAT_CLR, WAGO_Y[0]+1, -1, WAGO_TOP+USB_CLR))
    if hy > WAGO_Y[1] and hy-BOSS_D/2 < WAGO_Y[1]+BOSS_FLAT_CLR:
        lid = lid.cut(box(hx-BOSS_D, hx+BOSS_D, WAGO_Y[1]-1, WAGO_Y[1]+BOSS_FLAT_CLR, -1, WAGO_TOP+USB_CLR))
# Wago push-button access slots through the plate
for (x0,x1,y0,y1) in BTN_SLOTS:
    lid = lid.cut(box(x0,x1,y0,y1, Z_WALL_TOP-LIP_H-1, Z_LID_TOP+1))
try:
    top=[e for e in lid.Edges if abs(e.BoundBox.ZMin-Z_LID_TOP)<1e-6 and abs(e.BoundBox.ZMax-Z_LID_TOP)<1e-6 and e.Length>3 and (abs(e.BoundBox.XMin-ox0)<1e-6 or abs(e.BoundBox.XMax-ox1)<1e-6 or abs(e.BoundBox.YMin-oy0)<1e-6 or abs(e.BoundBox.YMax-oy1)<1e-6)]
    lid = lid.makeChamfer(0.6, top)
except Exception as ex: print("lid chamfer skipped:", ex)

base = base.removeSplitter(); lid = lid.removeSplitter()

# ---------------- screws: M2.5 x 10 pan head, driven from below ----------------
# head in the floor counterbore -> shank through floor, pillar and the 3 mm board hole -> self-taps into the lid boss
Z_HEAD = Z_FLOOR_BOT+CB_DEPTH          # underside of the head rests on the counterbore bottom
Z_TIP  = Z_HEAD+SCREW_L
def screw(hx,hy):
    s = cyl(HEAD_D, HEAD_H, V(hx,hy,Z_HEAD-HEAD_H))
    for (dx,dy) in ((0.35,1.5),(1.5,0.35)):                                   # cross recess
        s = s.cut(box(hx-dx,hx+dx,hy-dy,hy+dy, Z_HEAD-HEAD_H-0.1, Z_HEAD-HEAD_H+0.9))
    s = s.fuse(cyl(SCREW_D, SCREW_L-0.5, V(hx,hy,Z_HEAD)))
    s = s.fuse(Part.makeCone(SCREW_D/2, SCREW_D/2-0.5, 0.5, V(hx,hy,Z_TIP-0.5)))
    return s.removeSplitter()
screws = [screw(hx,hy) for (hx,hy) in HOLES]
print("SCREW head Z %.1f..%.1f (case bottom %.1f), tip Z %.1f, pilot bottom Z %.1f, thread engagement %.1f mm" %
      (Z_HEAD-HEAD_H, Z_HEAD, Z_FLOOR_BOT, Z_TIP, BOSS_DEPTH, Z_TIP))
print("VALID base", base.isValid(), "lid", lid.isValid(), "solids", len(base.Solids), len(lid.Solids))
print("VOL base %.0f mm3  lid %.0f mm3" % (base.Volume, lid.Volume))
bb=base.BoundBox; print("BASE bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
bb=lid.BoundBox;  print("LID  bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))

# ---------------- populated board from the KiCad STEP export ----------------
# KiCad writes the export in layout coordinates: X as drawn, Y negated, Z=0 at the board bottom with the
# components seated at 1.595 (1.51 mm dielectric plus copper). Shift that into the board frame used here.
# The through-hole pins are cut flush on the real board, so everything below the board bottom is removed.
PCB_X0, PCB_Y0, PCB_Z0 = 140.265, 63.255, 1.595
DNP = {"R3"}      # footprints that are not populated on the boards (R3: RT left floating)
# ---------------- reference designators from the KiCad board file ----------------
def kicad_refs(path):
    """[(reference, x, y)] for every footprint in the .kicad_pcb, origin in the board frame used here."""
    if not os.path.exists(path): return []
    t=open(path, encoding="utf-8").read(); out=[]; i=0; n=len(t)
    while True:
        i=t.find("(footprint ", i)
        if i<0: break
        depth=0; j=i; q=False; at=None
        while j<n:                                   # matching close paren, skipping quoted strings
            ch=t[j]
            if q:
                if ch=="\\": j+=1
                elif ch=='"': q=False
            elif ch=='"': q=True
            elif ch=="(":
                depth+=1
                if depth==2 and at is None and t.startswith("(at ", j):      # the footprint's own position
                    at=re.match(r"\(at (-?[\d.]+) (-?[\d.]+)", t[j:j+60])
            elif ch==")":
                depth-=1
                if depth==0: break
            j+=1
        r=re.search(r'\(property "Reference" "([^"]*)"', t[i:j+1])
        if at and r and r.group(1) and not r.group(1).startswith("G"):
            out.append((r.group(1), float(at.group(1))-PCB_X0, PCB_Y0-float(at.group(2))))
        i=j+1
    return out
REFS = kicad_refs(os.path.join(os.getcwd(), "USB-Adapter.kicad_pcb"))
def refdes(sh):
    """reference whose footprint origin lies inside the part's footprint, nearest the part centre"""
    bb=sh.BoundBox; cx,cy=bb.Center.x,bb.Center.y
    hits=[(math.hypot(x-cx,y-cy), r) for (r,x,y) in REFS if bb.XMin-0.3<=x<=bb.XMax+0.3 and bb.YMin-0.3<=y<=bb.YMax+0.3]
    return min(hits)[1] if hits else ""

board = rrect(0,0,BW,BL,BR,-BT,BT)                         # fallback outline if the export is missing
for (hx,hy) in HOLES: board = board.cut(cyl(3.0, BT+2, V(hx,hy,-BT-1)))
comps = {"L1 7070 envelope": box(19.085-4.15,19.085+4.15,6.755-4.15,6.755+4.15,0,7.3)}  # fitted part is a 7070, the KiCad model is a 6060
pcb_parts = []
if os.path.exists(PCB_STEP):
    import Import
    pdoc = FreeCAD.newDocument("pcb"); Import.insert(PCB_STEP, "pcb")
    flush = box(-5, BW+10, -5, BL+5, -BT, 30)
    objs = [o for o in pdoc.Objects if hasattr(o,"Shape") and o.Shape.Solids and o.Shape.BoundBox.XMin > 100]
    whole = max(objs, key=lambda o: len(o.Shape.Solids))     # the top-level assembly compound
    for o in objs:
        if o is whole: continue
        sh = o.Shape.copy(); sh.translate(V(-PCB_X0, PCB_Y0, -PCB_Z0)); sh = sh.common(flush)
        if sh.Volume < 1e-6: continue
        if sh.Volume > 900: board = sh; pcb_parts.append(("PCB", sh)); continue
        label = re.sub(r"(Metric)\d{3}$", r"\1", o.Label)          # drop KiCad's duplicate-model suffix
        ref = refdes(sh)
        if ref in DNP: continue
        label = (ref+" "+label).strip()
        pcb_parts.append((label, sh)); comps[label] = sh
    FreeCAD.closeDocument(pdoc.Name)
    zs=[sh.BoundBox for n,sh in pcb_parts]
    print("PCB STEP: %d parts, Z %.2f..%.2f in the board frame after removing everything below the board bottom" %
          (len(pcb_parts), min(b.ZMin for b in zs), max(b.ZMax for b in zs)))
else:
    print("USB-Adapter.step not found: checking the board outline and inductor envelope only")
comps["board"] = board
worst = 99
for name,sh in comps.items():
    for cname,c in (("base",base),("lid",lid)):
        try:
            v=c.common(sh).Volume; d=0.0 if v>1e-6 else c.distToShape(sh)[0]
        except Exception as ex:
            v=float('nan'); d=float('nan'); print("  check failed", name, cname, ex)
        if name!="board": worst=min(worst,d)
        print(f"CHECK {name:28} vs {cname}: overlap {v:7.3f} mm3   clearance {d:5.2f} mm")
print("CLOSEST component to the case: %.2f mm" % worst)
# screws: must clear base and board; the overlap with the lid is the material the thread cuts into
exp_eng = math.pi*((SCREW_D/2)**2-(BOSS_HOLE/2)**2)*Z_TIP
for i,s in enumerate(screws):
    print("SCREW %d vs base %.3f  vs board %.3f  vs lid %.1f mm3 (thread engagement, expected %.1f)" %
          (i+1, base.common(s).Volume, board.common(s).Volume, lid.common(s).Volume, exp_eng))

# ---------------- export ----------------
import Import, MeshPart, Mesh
doc=FreeCAD.newDocument("case")
def add(name,shape,group=None):
    o=doc.addObject("Part::Feature",name); o.Shape=shape; o.Label=name
    if group is not None: group.addObject(o)
    return o
# case only, assembled: base, lid and screws in their closed positions
oA=[add("Case_Base",base), add("Case_Lid",lid)]+[add("Screw_M2.5x10_%d"%(i+1), s) for i,s in enumerate(screws)]
doc.recompute()
Import.export(oA, OUT+"/usb-adapter-case-assembled.step")
# full assembly: case and populated board as a two-level STEP assembly, parts named by reference designator
asm=doc.addObject("App::Part","USB_Adapter"); asm.Label="USB-Adapter assembly"
grp=doc.addObject("App::Part","Case"); grp.Label="Case"; asm.addObject(grp)
add("Base", base, grp); add("Lid", lid, grp)
for i,s in enumerate(screws): add("Screw %d M2.5x10 pan head"%(i+1), s, grp)
pgrp=doc.addObject("App::Part","PCB"); pgrp.Label="PCB"; asm.addObject(pgrp)
named=[]
for n,sh in pcb_parts:
    label = "Board 40x18x1.6" if n=="PCB" else n+(" (fitted part is a 7070)" if n.startswith("L1 ") else "")
    if n!="PCB": named.append(label)
    add(label, sh, pgrp)
doc.recompute()
Import.export([asm], OUT+"/usb-adapter-assembly.step")
print("ASSEMBLY parts:", ", ".join(named))
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
allscrews = Part.makeCompound(screws)
exploded_screws = allscrews.copy(); exploded_screws.translate(V(0,0,-12))
parts = Part.makeCompound([sh for n,sh in pcb_parts if n!="PCB"]) if pcb_parts else None
prev={"base":tris(base),"lid":tris(exploded_lid),"board":tris(board),"ind":tris(comps["L1 7070 envelope"]),"lid_closed":tris(lid),
      "screws":tris(exploded_screws),"screws_closed":tris(allscrews)}
if parts: prev["parts"]=tris(parts)
# half section: keep Y >= board centre line, which cuts through the third screw and the cable hole
half = box(ox0-5, ox1+10, BL/2, oy1+5, Z_FLOOR_BOT-5, Z_LID_TOP+5)
secs = {"base":base,"lid":lid,"board":board,"screws":allscrews,"ind":comps["L1 7070 envelope"]}
if parts: secs["parts"]=parts
for k,sh in secs.items():
    try: prev[k+"_sec"]=tris(sh.common(half))
    except Exception as ex: print("section failed", k, ex)
if os.environ.get("PREVIEW_JSON"): json.dump(prev, open(os.environ["PREVIEW_JSON"],"w"))
json.dump({"outer_mm":[round(ox1-ox0,1),round(oy1-oy0,1),round(Z_LID_TOP-Z_FLOOR_BOT,1)],"wall":WALL,"floor":FLOOR,"lid":LID_T,
           "usb_protrusion_mm":round(44.88-ox1,1),"standoff":STAND,"wire_end_extension":EXT,"cable_hole_mm":CABLE_D,
           "screws":"3x M2.5 x 10 pan-head self-tapping, from below; counterbore %.1f mm, pilot hole %.1f mm x %.1f mm deep" % (CB_DEPTH, BOSS_HOLE, BOSS_DEPTH)}, open(OUT+"/case-dimensions.json","w"), indent=1)
print("DONE")

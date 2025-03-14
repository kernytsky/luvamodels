from build123d import *
from ocp_vscode import *
set_port(3939)

levels = 6

l_start = 28
l_step = -4
l_end = l_start + levels * l_step 

w_start = 32 #32
w_step = -5
w_end = w_start + levels * w_step

h = 30

slot_w = 6+3
slot_h = 6

helix_pitch = 470
helix_height = 470
helix_rad = 50

sk = Sketch()
for l, w in zip(range(l_start, l_end-1, l_step), range(w_start, w_end-1, w_step)):
    wall_width = 1.6 if w == w_start else 0.6
    print(l, w, wall_width)
    sk = sk + Ellipse(l, w) - Ellipse(l - wall_width, w - wall_width)

slot_rot = Rot(0, 0, 90)
sk -= slot_rot * SlotCenterToCenter(slot_w, slot_h + 5) # make clear area for slot
# make wall for slot; width of 1mm / 2 leads to sometimes crossing the 0.5 boundary so made 0.95
sk += slot_rot * SlotCenterToCenter(slot_w, slot_h + 0.4) - slot_rot * SlotCenterToCenter(slot_w, slot_h) 

# make sweep path for helix
hx = Helix(helix_pitch, helix_height, helix_rad)
hx_start = Pos(helix_rad, 0, 0) * Rot(0, 0, 0) * sk # * Rectangle(5, 5)
#show(hx, hx_start)
lamp = sweep(hx_start, hx, is_frenet=True)

# Make flat cut at the bottom
lamp -= Box(300, 300, 40)

pedastal_rad = 80.1
pedastal_height = 6
groove_tol = 0.2

#.cylinder(pedastal_height, pedastal_rad, centered =[True, True, False])

aln_minz = align = (Align.CENTER, Align.CENTER, Align.MIN)
pedastal = Cylinder(pedastal_rad, pedastal_height, align = aln_minz)
pedastal = fillet(pedastal.edges().group_by(Axis.Z)[-1], 2)
pedastal -= extrude(Circle(pedastal_rad - 1.5 + groove_tol, align = aln_minz) -
                    Circle(pedastal_rad - 3 - groove_tol, align = aln_minz), 1)

p_boreRad = 1.5  # Diameter of the counterbore hole, if any
p_boreDepth = 4  # Depth of the counterbore hole, if
p_screwpostOD = 10
screw_rad_base = 72 # Screw hole radius from base of center

ped_wp = Plane(pedastal.faces().sort_by(Axis.Z).first)
pedastal -= (ped_wp * PolarLocations(radius=screw_rad_base, count=3, start_angle=0, angular_range=360)
    * Hole(p_boreRad, p_boreDepth))
pedastal -= Pos(0, - pedastal_rad + 4) * Sphere(3 + .1)

res = Pos(0, 0, 14) * pedastal + lamp

# make cut for slot
slot_cut_sk = Pos(helix_rad, 0, 0) * Rot(0, 0, 0) * slot_rot * SlotCenterToCenter(slot_w, slot_h)
slot_cut = sweep(slot_cut_sk, hx, is_frenet=True)
res -= slot_cut

if False:
    #res = res & Pos(0, 0, 50) * Box(300, 300, 100, mode=Mode.INTERSECT)
    res = res & Pos(45, 20, 19) * Cylinder(50, 30, mode=Mode.INTERSECT, align=aln_minz)

# add the tip
#res = res + Plane(res.faces().sort_by(Axis.Z).last) * Pos(0,0,5) * Sphere(33, 30) #.extrude(10)
tip = extrude(Plane(slot_cut.faces().sort_by(Axis.Z).last) * Pos(0,0,0) * Ellipse(l_start, w_start), 2)
#tip = fillet(tip.edges().group_by(Axis.Z)[-1], 1)
res = res + tip
res = fillet(res.edges().group_by(Axis.Z)[-1], 1.9)

show(res)
export_stl(res, "models/helix_lamp_0.6.stl")
from build123d import *
from ocp_vscode import *
set_port(3939)

slot_w = 6+3
slot_h = 6

helix_pitch = 470
helix_height = 40
helix_rad = 48

def make_circle_sketch(levels = 6, ext_wall_width=1.6,l_start=30, l_step=-4, w_start=31, w_step=-5):
    l_end = l_start + levels * l_step
    w_end = w_start + levels * w_step

    # make circle with slot in it that is swept into the lamp shape
    sk = Sketch()
    for l, w in zip(range(l_start, l_end-1, l_step), range(w_start, w_end-1, w_step)):
        wall_width = ext_wall_width if w == w_start else 0.6
        print(l, w, wall_width)
        sk = sk + Ellipse(l, w) - Ellipse(l - wall_width, w - wall_width)
    return sk

def make_cactus_sketch(solid=False):
    radius=32.5

    arcd = 2
    arcs = 8
    topangd = 90
    topangs = -topangd - 30

    #last = Line((-35, -2), (-34, -1))
    # last = RadiusArc(start_point=(-radius, -2), end_point=(-radius, 2), radius=arcs)
    last = JernArc(start=(-radius, 0), tangent=(0, 1), radius=arcs, arc_size=topangs/2)
    sprof = Curve()

    for i in range(12):
        l1 = JernArc(start=last @ 1, tangent=last % 1, radius=arcd / 2, arc_size=topangd)
        l2 = JernArc(start=l1 @ 1, tangent=l1 % 1, radius=arcs, arc_size=topangs)
        sprof += (l1, l2)
        last = l2

    cact = make_face(sprof)
    if not solid:
        cact -= make_face(offset(sprof, -1.6))
    cact = scale(cact, (0.93, .97, 1))
    return cact

#sk = make_circle_sketch()
sk = make_circle_sketch(levels=5, ext_wall_width=0.6, l_start=25, l_step=-4, w_start=26, w_step=-5)
sk += make_cactus_sketch()
# show(sk, reset_camera=Camera.KEEP)
# raise SystemExit

slot_rot = Rot(0, 0, 90)
sk -= slot_rot * SlotCenterToCenter(slot_w, slot_h + 5) # make clear area for slot
# make wall for slot; width of 1mm / 2 leads to sometimes crossing the 0.5 boundary so made 0.95
sk += slot_rot * SlotCenterToCenter(slot_w, slot_h + 0.4) - slot_rot * SlotCenterToCenter(slot_w, slot_h) 

# make sweep path for helix
hx = Helix(helix_pitch, helix_height, helix_rad)
hx_start = Pos(helix_rad, 0, 0) * Rot(0, 0, 0) * sk # * Rectangle(5, 5)
#show(hx, hx_start)
lamp = sweep(hx_start, hx, is_frenet=True)

# Make flat cut at the bottom of the lamp
lamp -= Box(300, 300, 40)

# Create base that interfaces with the pedastal
expansion_adjust = 0.0 # amount to expand the base to adjust for shrinkage compared to the base
pedastal_rad = 80.1 + expansion_adjust
pedastal_height = 6
groove_tol = 0.2

aln_minz = align = (Align.CENTER, Align.CENTER, Align.MIN)
pedastal = Cylinder(pedastal_rad, pedastal_height, align = aln_minz)
pedastal = fillet(pedastal.edges().group_by(Axis.Z)[-1], 2)
pedastal -= extrude(Circle(pedastal_rad - 1.5 + groove_tol, align = aln_minz) -
                    Circle(pedastal_rad - 3 - groove_tol, align = aln_minz), 1)

# Make screw holes
p_boreRad = 1.5  # Diameter of the counterbore hole, if any
p_boreDepth = 4  # Depth of the counterbore hole, if
p_screwpostOD = 10
screw_rad_base = 72 + expansion_adjust # Screw hole radius from base of center

ped_wp = Plane(pedastal.faces().sort_by(Axis.Z).first)
pedastal -= (ped_wp * PolarLocations(radius=screw_rad_base, count=3, start_angle=0, angular_range=360)
    * Hole(p_boreRad, p_boreDepth))
pedastal -= Pos(0, - pedastal_rad + 4) * Sphere(3 + .1) # add centering bump

res = Pos(0, 0, 14) * pedastal + lamp

# make cut for slot
slot_cut_sk = Pos(helix_rad, 0, 0) * Rot(0, 0, 0) * slot_rot * SlotCenterToCenter(slot_w, slot_h)
slot_cut = sweep(slot_cut_sk, hx, is_frenet=True)
res -= slot_cut

# add the tip
#res = res + Plane(res.faces().sort_by(Axis.Z).last) * Pos(0,0,5) * Sphere(33, 30) #.extrude(10)
#tip = extrude(Plane(slot_cut.faces().sort_by(Axis.Z).last) * Pos(0,0,0) * Ellipse(l_start, w_start), 2)

tip = extrude(Plane(slot_cut.faces().sort_by(Axis.Z).last) * Pos(0,0,0) * make_cactus_sketch(solid=True), 2)
res = res + tip
res = fillet(res.edges().group_by(Axis.Z)[-1], 1.9)

if True:
    res = res & Pos(0, 0, 0) * Box(300, 300, 17, mode=Mode.INTERSECT, align=aln_minz)
    #res = res & Pos(0, 0, 6) * Box(300, 300, 100, mode=Mode.INTERSECT, align=aln_minz)
    #res = res & Pos(50, 30, 19.4) * Cylinder(55, 50, mode=Mode.INTERSECT, align=aln_minz)

show(res, reset_camera=Camera.KEEP)
export_stl(res, "models/helix_lamp_0.6.stl")
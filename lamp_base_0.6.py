from build123d import *
from ocp_vscode import *
set_port(3939)

from pathlib import Path
from math import cos, sin, radians

### 0.6 changes:
# Flip screw holes 180 to match new lamp body
# Adjust button hole locations for new switches on PCB

### 0.5 changes:
# Make screw holes 120 degrees apart

pedastal_rad = 80.1
base_thickness = 1
inset_width = 3
inset_height = 3
wall_thickness = 1
base_rad = pedastal_rad + wall_thickness
base_height = 18.5
power_rad = 3.5  # 7
button_rad = 1.5 + 1  # 4



# Function to create snap fit mounts
def make_snap_fit(x, y, h, r):
    pts = (Circle(r),
            Pos(0, 0, 3.3) * Circle(r),
            Pos(0, 0, 3.8+0.6) * Ellipse(r * 1.08, r),
            Pos(0, 0, 3.8+0.6+h*0.25) * Circle(r * 0.5)
    )
    snap = loft(Sketch() + pts, ruled=True)           

    # Create cutout box, subtract it, and move the box to the correct location
    cutout_box = Box(r * 0.5, r * 4, h * 1.9, align=(Align.CENTER, Align.CENTER, Align.MIN))
    snap_fit = Pos(x, y) * (snap - cutout_box)
    
    return snap_fit


# Create the base outer shell as a cylinder
base_shell = Cylinder(base_rad, base_height, 
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
base_shell = Rot(180, 0, 0) * base_shell #.rotated(Axis.X_AXIS, 180)

# Add ledge at top where lamp body sits
groove_od = 1.5 # groove offsets from pedastal_rad 
tol = 0.1  # tolerance for fitting lamp

top_face = base_shell.faces().sort_by(Axis.Z)[-1]
top_plane = Plane(top_face)

outer_circle = Circle(pedastal_rad + wall_thickness - groove_od - tol, align=(Align.CENTER, Align.CENTER))
inner_circle = Circle(pedastal_rad + wall_thickness - inset_width + tol, align=(Align.CENTER, Align.CENTER))
ledge_ring = outer_circle - inner_circle
ledge_ring = ledge_ring.located(Location((0, 0, 0))) #base_height)))
ledge = extrude(ledge_ring, 1)

base = base_shell + ledge

# Create cutout for the main cavity
fillet_rad = 2
pizza_depth = 0.6
top_circle = Circle(pedastal_rad + wall_thickness - inset_width + tol)
middle_circle = Pos(0, 0, -inset_height) * Circle(pedastal_rad)
bottom_circle = Pos(0, 0, -base_height + base_thickness) * Circle(pedastal_rad)
cavity = loft(Sketch() + [top_circle, middle_circle, bottom_circle], ruled=True)
cavity = fillet(cavity.edges().group_by(Axis.Z)[0], fillet_rad) # Add fillets to the bottom interior
base = base - cavity
base = fillet(base.edges().sort_by(Axis.Z)[0], fillet_rad) # Add fillets to the bottom exterior

#show(pizza)

# Create breadboard mount points
#mounts = ((45, 30), (90, 30)), (45, 79), (90, 79))
mounts = ((89, 30), (89, 79))
mount_r = 3
mount_h = 8
mount_dx = -pedastal_rad - 29
mount_dy = -54.5

for mount in mounts:
    mount_x = mount[0] + mount_dx
    mount_y = mount[1] + mount_dy
    mount_z = -base_height + base_thickness
    snap_part = make_snap_fit(mount_x, mount_y, mount_h, mount_r)
    snap_part = snap_part.located(Location((mount_x, mount_y, mount_z)))
    base = base + snap_part
#show(base)

# Create PCB box
bbb_width = 60.5 - 3
bbb_height = 61 - 4
pts = [(0, 0), (bbb_width, 0), (bbb_width, bbb_height), (0, bbb_height)]

profile = Plane.YZ * Rectangle(1, 2, align=(Align.CENTER, Align.MIN))
path = Plane.XY * Polyline(*pts)
bbb = sweep(profile, path, transition=Transition.ROUND)
bbb = bbb.located(Location((-73, -28.5, -base_height + base_thickness)))
base = base + bbb
#show(bbb, base)


# Create button holes
#butts = [(35.75, -36.7 + 0.5, 76), (33.85, -48.15, 84), (33.7, -60.45 - 1, 94)]
butts = [(35.75, -36.7 + 0.5), (33.85, -48.15 - 1.5), (33.7, -60.45 - 1 - 1.5)]
for butt in butts:
    x = butt[0] - 106
    y = butt[1] + 56 + 1.5
    button_hole = Cylinder(button_rad, base_rad, rotation=(0, -90, 0), 
                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    button_hole = button_hole.located(Location((x, y, -base_height + 9))) # -19)))
    base = base - button_hole

# Create power button hole
powers = [(46.05, -67.05, -78)]
for power in powers:
    x = -59.95
    y = -16.05
    z = -base_height + 11
    power_hole = Cylinder(button_rad * 1.6, base_rad, rotation=(0, -90, 0),
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    power_hole = power_hole.located(Location((x, y, z)))
    base = base - power_hole

# Add centering bump
center_bump_cylinder = Pos(0, -pedastal_rad + 4, 0) * Cylinder(3, base_height - base_thickness, 
                               rotation=(180, 0, 0), align=(Align.CENTER, Align.CENTER, Align.MIN))
center_bump_sphere = Pos(0, -pedastal_rad + 4, 0) * Sphere(3)
base = base + center_bump_cylinder + center_bump_sphere
#show(base, position=(-100, 0, -13), ortho=True)
#export_stl(base, "lamp_base_5.2.stl")


# Create screw posts
# p_screwpostID = 5.0
p_screwpostOD = 7.5
p_cBoreRad = 4.5
p_boreDepth = 4.0
screw_rad_base = 70
p_boreRad = 2.5
screw_rad_base = 72 # Screw hole radius from base of center

#ped_wp = Plane(base.faces().sort_by(Axis.Z)[0])
screw_plane = Plane(base.faces().sort_by(Axis.Z)[0]) 
screw_points1 = PolarLocations(radius=screw_rad_base, count=3, start_angle=0, angular_range=360)
screw_points = screw_plane * screw_points1
snapshot = base.edges()
base += screw_points * Cylinder(p_screwpostOD / 2.0, base_height ,
                align=(Align.CENTER, Align.CENTER, Align.MAX))
base_z = -base_height + base_thickness
base = chamfer((base.edges() - snapshot).filter_by_position(Axis.Z, base_z, base_z, inclusive=(True, True)), 2.5)
base -= screw_points * Hole(3.5, 2)
#Pos(0, 0, 2)


l1 = CenterArc((0, 0, -inset_height), pedastal_rad + pizza_depth, 155, 50)
l2 = Line((l1 @ 1), (0, 0, -inset_height))
l3 = Line((l1 @ 0), (0, 0, -inset_height))
pizza = make_face(Curve() + [l1, l2, l3])
pizza = extrude(pizza, -12.5)
base -= pizza

# Create wedge to hold PCB in place
wedge_w = 1.2
wedge_prof = make_face(Polyline((0, 0), (wedge_w, 0.5), (wedge_w, 2), (0, 2), (0, 0)))
#bbb_top_prof = Pos(-pedastal_rad + wall_thickness, 0, -23) * (Plane.XZ * Rectangle(2, 2, align=(Align.CENTER, Align.MIN)))
bbb_top_prof = Pos(-pedastal_rad - pizza_depth, 0, -base_height + 4.7) * (Plane.XZ * wedge_prof)
bbb_top_path = CenterArc((0, 0), pedastal_rad + 2, 157, 27)
bbb_top = sweep(bbb_top_prof, bbb_top_path)#, transition=Transition.ROUND)
base = base + bbb_top


#screw_plane * Pos(0, 0, 2) * screw_points

#base2 = []

#x# = PolarLocations(radius=screw_rad_base, count=3, start_angle=0, angular_range=360)
#x = Plane(base.faces().sort_by(Axis.Z)[0]) * x
base -= screw_plane * Pos(0, 0, -1.5) * screw_points1 * CounterSinkHole(p_boreRad, p_cBoreRad, base_height, counter_sink_angle=75)

#base -= Pos(0, - pedastal_rad + 4) * Sphere(3 + .1)
#res = Pos(0, 0, 14) * pedastal + lamp

# Test section (controlled by test flag)
test = False

if test:
    # test_box = Box(20, 28, 60, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # test_box = test_box.located(Location((0, -80, -20)))
    test_box = Box(100, 74, 60, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    test_box = test_box.located(Location((-60, 0, -20)))
    #test_box = Box(30, 80, 60, align=(Align.CENTER, Align.MIN, Align.MIN))
    #test_box = test_box.located(Location((70, -70, -50)))
    base = base.intersect(test_box)

# Export to STL
# show(base, position=(50, 0, 39)) # from right
#show(base, position=(-20, -80, -5)) # from front
#show(base, position=(-120, 0, -15)) # from left
#show(base, position=(0, 0, 100)) # from top
show(base, reset_camera=Camera.KEEP)
export_stl(base, "models/lamp_base_6.stl")
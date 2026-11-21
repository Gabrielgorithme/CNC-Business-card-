"""Renders preview images of the engraved mock-up (run under xvfb-run).
Colour is tinted by depth below the nearest face so shallow engraving stays readable."""
import pyvista as pv, numpy as np, pathlib
from matplotlib.colors import LinearSegmentedColormap
out = pathlib.Path(__file__).parent.parent / "design" / "v2" / "3d"
m = pv.read(str(pathlib.Path(__file__).parent / "card_v2_engraved.stl"))
z = m.points[:, 2]
m["depth"] = np.clip(np.minimum(z, 2.0 - z), 0, 0.3)
m = m.compute_normals(split_vertices=True, feature_angle=35)
cmap = LinearSegmentedColormap.from_list("alu", [(0, "#d3d7dc"), (0.3, "#8d939b"), (1, "#4a4f56")])
c = np.array(m.center)
def shot(name, pos, up, zoom=1.0, focus=None, mesh=m, size=(1800, 1200), rake=(-1, .6, .35)):
    p = pv.Plotter(off_screen=True, window_size=size, lighting="none"); p.set_background("#17191c")
    p.add_mesh(mesh, scalars="depth", cmap=cmap, clim=(0, 0.3), show_scalar_bar=False, smooth_shading=True,
               ambient=0.32, diffuse=0.62, specular=0.5, specular_power=40)
    f = c if focus is None else np.array(focus)
    side = 1 if pos[2] > 0 else -1
    p.add_light(pv.Light(position=tuple(f + 300 * np.array([rake[0], rake[1], rake[2] * side])), focal_point=tuple(f), intensity=1.0))
    p.add_light(pv.Light(position=tuple(f + np.array(pos)), focal_point=tuple(f), intensity=0.45))
    p.camera.position = tuple(f + np.array(pos)); p.camera.focal_point = tuple(f); p.camera.up = up
    p.camera.view_angle = 22; p.camera.zoom(zoom); p.enable_anti_aliasing("ssaa")
    p.screenshot(str(out / name)); p.close()
shot("recto.png", (-30, -90, 150), (0, 0, 1), 1.2)
shot("verso.png", (30, -90, -150), (0, 0, -1), 1.2)
shot("verso_top.png", (0, -1, -250), (0, 1, 0), 1.0, size=(2000, 1300))
shot("recto_top.png", (0, -1, 250), (0, 1, 0), 1.0, size=(2000, 1300))
shot("spring_closeup.png", (-14, -42, 48), (0, 0, 1), 1.0, focus=(59, 31.98, 1))

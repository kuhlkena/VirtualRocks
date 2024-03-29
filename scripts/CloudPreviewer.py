import sys
import open3d

# VirtualRocks source is released under GPL-3.0-only or GPL-3.0-or-later

def show(filename):
    """
    Function to open an open3d viewer window of a .ply file. Called as a subprocess in 
    :ref:`main <main>`.

    Args:
        filename (string): Path to the .ply file the user wants to preview.
    """
    cloud = open3d.io.read_point_cloud(filename)
    open3d.visualization.draw_geometries([cloud])

# Get args from caller (Main) and start open3d preview
file = sys.argv[1]
try:
    show(file)
except Exception as e:
    print(e, flush=True)
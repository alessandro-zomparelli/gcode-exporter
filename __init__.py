# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# ----------------------------- GCODE EXPORTER ------------------------------- #
#                                                                              #
#                            Alessandro Zomparelli                             #
#                                   (2020)                                     #
#                                                                              #
# http://www.co-de-it.com/                                                     #
# http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Mesh/Tissue      #
#                                                                              #
# ############################################################################ #

bl_info = {
    "name": "Gcode Exporter",
    "author": "Alessandro Zomparelli (Co-de-iT)",
    "version": (0, 1, 00),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Export edges paths or polylines as gcode files for digital fabrication",
    "warning": "",
    "wiki_url": "https://github.com/alessandro-zomparelli/gcode_exporter/wiki",
    "tracker_url": "https://github.com/alessandro-zomparelli/gcode_exporter/issues",
    "category": "Import-Export"}


if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    importlib.reload(gcode_export)

else:
    from . import utils
    from . import gcode_export

import bpy
from bpy.props import PointerProperty, CollectionProperty, BoolProperty

classes = (
    gcode_export.GCODE_PT_gcode_exporter,
    gcode_export.gcode_settings,
    gcode_export.gcode_export
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gcode_settings = PointerProperty(
                                            type=gcode_export.gcode_settings
                                            )

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

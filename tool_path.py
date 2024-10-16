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

import numpy as np
import mathutils

class ToolPath():
    vertices = None
    layer_height = None
    speed = None
    is_cyclic = None

    def __init__ (self, vertices=None, cyclic=None, layer_heights=None, speeds=None):
        self.vertices = vertices
        self.is_cyclic = cyclic
        self.layer_height = layer_heights
        self.speed = speeds

    def make_cyclic(self):
        if not self.is_cyclic: return
        for i, is_curve_cyclic in enumerate(self.is_cyclic):
            if is_curve_cyclic:
                self.vertices[i] += [self.vertices[i][0],]
                if self.layer_height:
                    self.layer_height[i] += [self.layer_height[i][0],]
                if self.speed:
                    self.speed[i] += [self.speed[i][0],]
    
    def sort_z(self):
        sorted_verts = []
        if self.layer_height:
            sorted_height = []
        if self.speed:
            sorted_speed = []
        for i, curve in enumerate(self.vertices):
            # mean z
            listz = [v[2] for v in curve]
            meanz = np.mean(listz)
            # store curve and meanz
            sorted_verts.append((curve, meanz))
            if self.layer_height:
                sorted_height.append((self.layer_height[i], meanz))
            if self.speed:
                sorted_speed.append((self.speed[i], meanz))
        self.vertices = [data[0] for data in sorted(sorted_verts, key=lambda height: height[1])]
        if self.layer_height:
            self.layer_height = [data[0] for data in sorted(sorted_height, key=lambda height: height[1])]
        if self.speed:
            self.speed = [data[0] for data in sorted(sorted_speed, key=lambda height: height[1])]

    def sort_xy(self, mode='CONT'):
        median_points = [np.mean(verts,axis=0) for verts in self.vertices]
        for j, curve in enumerate(self.vertices):
            # for closed curves finds the best starting point
            if self.is_cyclic[j]:
                # create kd tree
                kd = mathutils.kdtree.KDTree(len(curve))
                for i, v in enumerate(curve):
                    kd.insert(v, i)
                kd.balance()

                if mode == 'RETR':
                    if j==0:
                        # close to next two curves median point
                        co_find = np.mean(median_points[j+1:j+3],axis=0)
                    elif j < len(self.vertices)-1:
                        co_find = np.mean([median_points[j-1],median_points[j+1]],axis=0)
                    else:
                        co_find = np.mean(median_points[j-2:j],axis=0)
                else:
                    if j==0:
                        # close to next two curves median point
                        co_find = np.mean(median_points[j+1:j+3],axis=0)
                    else:
                        co_find = self.vertices[j-1][-1]
                co, index, dist = kd.find(co_find)
                self.vertices[j] = self.vertices[j][index:] + self.vertices[j][:index+1]
                if self.layer_height:
                    self.layer_height[j] = self.layer_height[j][index:] + self.layer_height[j][:index+1]
                if self.speed:
                    self.speed[j] = self.speed[j][index:] + self.speed[j][:index+1]
            else:
                if j > 0:
                    p0 = curve[0]
                    p1 = curve[-1]
                    last = self.vertices[j-1][-1]
                    d0 = (last-p0).length
                    d1 = (last-p1).length
                    if d1 < d0:
                        self.vertices[j].reverse()
                        if self.layer_height:
                            self.layer_height[j].reverse()
                        if self.speed:
                            self.speed[j].reverse()
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

import bpy
import threading
import numpy as np
import multiprocessing
from multiprocessing import Process, Pool
from mathutils import Vector
try: from .numba_functions import numba_lerp2
except: pass

weight = []
n_threads = multiprocessing.cpu_count()

def find_curves(edges, n_verts):
    verts_dict = {key:[] for key in range(n_verts)}
    for e in edges:
        verts_dict[e[0]].append(e[1])
        verts_dict[e[1]].append(e[0])
    curves = []
    while True:
        if len(verts_dict) == 0: break
        # next starting point
        v = list(verts_dict.keys())[0]
        # neighbors
        v01 = verts_dict[v]
        if len(v01) == 0:
            verts_dict.pop(v)
            continue
        curve = []
        if len(v01) > 1: curve.append(v01[1])    # add neighbors
        curve.append(v)         # add starting point
        curve.append(v01[0])    # add neighbors
        verts_dict.pop(v)
        # start building curve
        while True:
            #last_point = curve[-1]
            #if last_point not in verts_dict: break

            # try to change direction if needed
            if curve[-1] in verts_dict: pass
            elif curve[0] in verts_dict: curve.reverse()
            else: break

            # neighbors points
            last_point = curve[-1]
            v01 = verts_dict[last_point]

            # curve end
            if len(v01) == 1:
                verts_dict.pop(last_point)
                if curve[0] in verts_dict: continue
                else: break

            # chose next point
            new_point = None
            if v01[0] == curve[-2]: new_point = v01[1]
            elif v01[1] == curve[-2]: new_point = v01[0]
            #else: break

            #if new_point != curve[1]:
            curve.append(new_point)
            verts_dict.pop(last_point)
            if curve[0] == curve[-1]:
                verts_dict.pop(new_point)
                break
        curves.append(curve)
    return curves

def curve_from_points(points, name='Curve'):
    curve = bpy.data.curves.new(name,'CURVE')
    for c in points:
        s = curve.splines.new('POLY')
        s.points.add(len(c))
        for i,p in enumerate(c): s.points[i].co = p.xyz + [1]
    ob_curve = bpy.data.objects.new(name,curve)
    return ob_curve

def curve_from_pydata(points, radii, indexes, name='Curve', skip_open=False, merge_distance=1, set_active=True):
    curve = bpy.data.curves.new(name,'CURVE')
    curve.dimensions = '3D'
    for c in indexes:
        # cleanup
        pts = np.array([points[i] for i in c])
        rad = np.array([radii[i] for i in c])
        if merge_distance > 0:
            pts1 = np.roll(pts,1,axis=0)
            dist = np.linalg.norm(pts1-pts, axis=1)
            count = 0
            n = len(dist)
            mask = np.ones(n).astype('bool')
            for i in range(n):
                count += dist[i]
                if count > merge_distance: count = 0
                else: mask[i] = False
            pts = pts[mask]
            rad = rad[mask]

        bool_cyclic = c[0] == c[-1]
        if skip_open and not bool_cyclic: continue
        s = curve.splines.new('POLY')
        n_pts = len(pts)
        s.points.add(n_pts-1)
        w = np.ones(n_pts).reshape((n_pts,1))
        co = np.concatenate((pts,w),axis=1).reshape((n_pts*4))
        s.points.foreach_set('co',co)
        s.points.foreach_set('radius',rad)
        s.use_cyclic_u = bool_cyclic
    ob_curve = bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(ob_curve)
    if set_active:
        bpy.context.view_layer.objects.active = ob_curve
    return ob_curve

def curve_from_vertices(indexes, verts, name='Curve'):
    curve = bpy.data.curves.new(name,'CURVE')
    for c in indexes:
        s = curve.splines.new('POLY')
        s.points.add(len(c))
        for i,p in enumerate(c): s.points[i].co = verts[p].co.xyz + [1]
    ob_curve = bpy.data.objects.new(name,curve)
    return ob_curve

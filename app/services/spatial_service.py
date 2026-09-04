from __future__ import annotations
from math import cos, radians, sqrt

def geometry_valid(geometry):
    """Validate the small EPSG:4326 demo geometries without requiring GIS services."""
    ring=_ring(geometry)
    if not geometry or geometry.get('type') not in ('Polygon','MultiPolygon') or len(ring)<4 or ring[0]!=ring[-1]: return False
    return all(isinstance(point,list) and len(point)>=2 and -180<=point[0]<=180 and -90<=point[1]<=90 for point in ring)

def _ring(geometry):
    if not geometry: return []
    coordinates = geometry.get("coordinates", [])
    if geometry.get("type") == "Polygon": return coordinates[0] if coordinates else []
    if geometry.get("type") == "MultiPolygon": return coordinates[0][0] if coordinates and coordinates[0] else []
    return []

def bbox(geometry):
    points = _ring(geometry)
    if not points: return None
    xs, ys = zip(*[(p[0], p[1]) for p in points])
    return min(xs), min(ys), max(xs), max(ys)

def area_hectares(geometry):
    """Local equirectangular projection, suitable for small demo polygons only."""
    points = _ring(geometry)
    if len(points) < 4: return 0.0
    lat0 = sum(p[1] for p in points) / len(points)
    factor_x, factor_y = 111_320 * cos(radians(lat0)), 110_540
    area = sum((points[i][0]*factor_x)*(points[i+1][1]*factor_y) - (points[i+1][0]*factor_x)*(points[i][1]*factor_y) for i in range(len(points)-1)) / 2
    return round(abs(area) / 10_000, 3)

def intersection_bbox(a, b):
    aa, bb = bbox(a), bbox(b)
    if not aa or not bb: return None
    x1,y1,x2,y2 = max(aa[0],bb[0]),max(aa[1],bb[1]),min(aa[2],bb[2]),min(aa[3],bb[3])
    if x1 >= x2 or y1 >= y2: return None
    return {"type":"Polygon", "coordinates":[[[x1,y1],[x2,y1],[x2,y2],[x1,y2],[x1,y1]]]}

def intersects(a,b): return intersection_bbox(a,b) is not None

def contains(a,b):
    outer,inner=bbox(a),bbox(b)
    return bool(outer and inner and outer[0]<=inner[0] and outer[1]<=inner[1] and outer[2]>=inner[2] and outer[3]>=inner[3])

def overlap_percent(a, b):
    total = area_hectares(a)
    hit = intersection_bbox(a, b)
    return round((area_hectares(hit) / total * 100), 2) if total and hit else 0.0

def centroid(geometry):
    points = _ring(geometry)
    if not points: return None
    return [sum(p[0] for p in points)/len(points), sum(p[1] for p in points)/len(points)]

def distance_m(a, b):
    pa, pb = centroid(a), centroid(b)
    if not pa or not pb: return None
    dx=(pa[0]-pb[0])*111_320*cos(radians((pa[1]+pb[1])/2)); dy=(pa[1]-pb[1])*110_540
    return round(sqrt(dx*dx+dy*dy), 1)

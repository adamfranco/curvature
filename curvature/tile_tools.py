import sys
import mercantile

# Class for building up an affected area from modified bounding-boxes.
class AffectedArea(object):

    def __init__(self):
        self.bbox = None

    # Record the bounding box of an affected area.
    #
    # bbox is decimal degrees with longitude -180 to +180 and Latitude -90 to +90.
    def record_affected(self, bbox):
        if self.bbox:
            self.bbox = self.bbox.union(bbox)
        else:
            self.bbox = bbox

    # Answer the affected bounding box
    def get_affected_bbox(self):
        return self.bbox

    # Answer the affected tiles at the zoom levels we're concerned with.
    #
    # Structure:
    #   [
    #     Tile(z=z0, x=x0, y=y0),
    #     Tile(z=z0, x=x1, y=y1),
    #     Tile(z=z0, x=x2, y=y2),
    #     Tile(z=z1, x=x3, y=y3),
    #     Tile(z=z1, x=x4, y=y4),
    #     ...
    #   ]
    def get_affected_tiles(self, max_zoom=20, min_zoom=None):
        # Add the tiles at the max zoom.
        affected_at_max = set(mercantile.tiles(
            self.bbox.west,
            self.bbox.south,
            self.bbox.east,
            self.bbox.north,
            [max_zoom],
            True))
        affected = affected_at_max

        # Recursively roll up affected tiles to lower zooms.
        if min_zoom is not None:
            z = max_zoom
            tiles = affected_at_max
            while z > min_zoom:
                tiles = self.roll_up_affected_tiles(tiles)
                z = z - 1
                affected = affected.union(tiles)

        return affected

    def roll_up_affected_tiles(self, tiles):
        affected = set()
        for tile in tiles:
            affected.add(mercantile.parent(tile))
        return affected

# BBox is decimal degrees with longitude -180 to +180 and Latitude -90 to +90.
class BBox(object):

    def __init__(self, west, south, east, north):
        # The minimum zoom-level to calculate affected tiles for.
        self.west = west
        self.south = south
        self.east = east
        self.north = north

    @classmethod
    def from_coords(cls, coords):
        bbox = None
        for coord in coords:
            coord_bbox = cls(coord[1], coord[0], coord[1], coord[0])
            if bbox is None:
                bbox = coord_bbox
            else:
                bbox = bbox.union(coord_bbox)
        return bbox

    # Return the union of two BBoxes.
    def union(self, bbox):
        unionNorth = max(self.north, bbox.north)
        unionSouth = min(self.south, bbox.south)
        unionWest = None
        unionEast = None

        # Case where bbox west intersects the range of current.
        myWidth = BBox.lon_distance_east(self.west, self.east)
        bboxWidth = BBox.lon_distance_east(bbox.west, bbox.east)
        if myWidth > BBox.lon_distance_east(self.west, bbox.west):
            # No need expand the bbox to the west
            unionWest = self.west
        # Case where curent west intersects the range of bbox.
        elif bboxWidth > BBox.lon_distance_east(bbox.west, self.west):
            # union west is that of the bbox.
            unionWest = bbox.west

        # Case where bbox east intersects the range of current.
        if myWidth > BBox.lon_distance_west(self.east, bbox.east):
            # No need expand the bbox to the west
            unionEast = self.east
        # Case where current east intersects the range of bbox.
        elif bboxWidth > BBox.lon_distance_west(bbox.east, self.east):
            # union east is that of the bbox.
            unionEast = bbox.east

        # If both east and west were overlapping the range of one of the boxes, we're done.
        if unionWest and unionEast:
            return BBox(unionWest, unionSouth, unionEast, unionNorth)

        # If the west side is overlapping, then we just need to pick our east.
        # This will be eastern edge furthest away from our western edge heading east.
        if unionWest:
            if BBox.lon_distance_east(unionWest, bbox.east) > BBox.lon_distance_east(unionWest, self.east):
                return BBox(unionWest, unionSouth, bbox.east, unionNorth)
            else:
                return BBox(unionWest, unionSouth, self.east, unionNorth)

        # If the east side is overlapping, then we just need to pick our west.
        # This will be western edge furthest away from our east edge heading west.
        if unionEast:
            if BBox.lon_distance_west(unionEast, bbox.west) > BBox.lon_distance_west(unionEast, self.west):
                return BBox(bbox.west, unionSouth, unionEast, unionNorth)
            else:
                return BBox(self.west, unionSouth, unionEast, unionNorth)

        # If we are still going here, our boxes don't overlap at all.
        # In this case we need to join them so that the distance between them is
        # minimized.
        # Measure the distance going west from each's west edge to the eastern
        # edge of the other.
        distanceA = BBox.lon_distance_west(self.west, bbox.east)
        distanceB = BBox.lon_distance_west(bbox.west, self.east)
        # if they are equally spaced, it doesn't matter, just pick one's west
        # and the other's east.
        if distanceA == distanceB:
            return BBox(self.west, unionSouth, bbox.east, unionNorth)
        # This means current sits closer to the east of bbox than vice versa.
        elif distanceA < distanceB:
            return BBox(bbox.west, unionSouth, self.east, unionNorth)
        # This means that current sits closer to the west of bbox.
        else:
            return BBox(self.west, unionSouth, bbox.east, unionNorth)

    def spans_antimeridian(self):
        return (self.west > self.east)

    # Calculate the longitudinal distance between two longitudes in degrees.
    @classmethod
    def min_lon_distance(cls, a, b):
        distance = (360 + a - b) % 360
        if distance > 180:
            return 360 - distance
        else:
            return distance

    # Calculate the longitudinal distance going west.
    @classmethod
    def lon_distance_west(cls, a, b):
        return (360 + a - b) % 360

    # Calculate the longitudinal distance going east.
    @classmethod
    def lon_distance_east(cls, a, b):
        return (360 + b - a) % 360

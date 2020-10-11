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

    # Return the union of two BBoxes.
    def union(self, bbox):
        unionNorth = max(self.north, bbox.north)
        unionSouth = min(self.south, bbox.south)
        # To-do: handle spanning +/- 180.
        unionWest = min(self.west, bbox.west)
        unionEast = max(self.east, bbox.east)
        return BBox(unionWest, unionSouth, unionEast, unionNorth)

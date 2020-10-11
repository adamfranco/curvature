# Add our parent folder to our path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from curvature.tile_tools import AffectedArea, BBox
from mercantile import Tile
import time

# Low-zoom tiles.
def tiles_at_zoom(tiles, zoom=0):
    tiles = list(filter(lambda t: t.z == zoom, tiles))
    return sorted(sorted(tiles, key=lambda tile: tile.y), key=lambda tile: tile.x)

def test_single_bbox():
    a = AffectedArea()
    a.record_affected(BBox(-73.2548, 43.9493, -73.0, 44.0461))

    b = a.get_affected_bbox()
    assert b.west == -73.2548, "West should be equal"
    assert b.south == 43.9493, "South should be equal"
    assert b.east == -73.0, "East should be equal"
    assert b.north == 44.0461, "North should be equal"

    tiles = a.get_affected_tiles(max_zoom=9, min_zoom=3)
    expected_tiles = {
        Tile(x=151, y=186, z=9),
        Tile(x=152, y=186, z=9),
        Tile(x=75, y=93, z=8),
        Tile(x=76, y=93, z=8),
        Tile(x=37, y=46, z=7),
        Tile(x=38, y=46, z=7),
        Tile(x=18, y=23, z=6),
        Tile(x=19, y=23, z=6),
        Tile(x=9, y=11, z=5),
        Tile(x=4, y=5, z=4),
        Tile(x=2, y=2, z=3)
    }
    assert tiles == expected_tiles

def test_overlapping_bboxes():
    a = AffectedArea()
    a.record_affected(BBox(-73.2548, 43.9493, -73.0, 44.0461))
    # Add an overlapping region.
    a.record_affected(BBox(-73.5, 44, -73.05, 44.7))

    b = a.get_affected_bbox()
    assert b.west == -73.5
    assert b.south == 43.9493
    assert b.east == -73.0
    assert b.north == 44.7

    tiles = a.get_affected_tiles(max_zoom=9, min_zoom=3)
    expected_tiles = {
        Tile(x=151, y=184, z=9),
        Tile(x=151, y=185, z=9),
        Tile(x=151, y=186, z=9),
        Tile(x=152, y=184, z=9),
        Tile(x=152, y=185, z=9),
        Tile(x=152, y=186, z=9),
        Tile(x=75, y=92, z=8),
        Tile(x=76, y=92, z=8),
        Tile(x=75, y=93, z=8),
        Tile(x=76, y=93, z=8),
        Tile(x=37, y=46, z=7),
        Tile(x=38, y=46, z=7),
        Tile(x=18, y=23, z=6),
        Tile(x=19, y=23, z=6),
        Tile(x=9, y=11, z=5),
        Tile(x=4, y=5, z=4),
        Tile(x=2, y=2, z=3)
    }
    assert tiles == expected_tiles

def test_many_bboxes_for_performance():
    a = AffectedArea()

    start_time = time.time()
    # Increment over 100,000 bboxes across 12°
    start_x = x = -112.44
    start_y = y = 31.93
    iterations = 100000
    deg = 12.0
    inc_deg = deg / iterations
    box_size = 0.3
    a.record_affected(BBox(x, y, x + box_size, y + box_size))
    for i in range(1, iterations + 1):
        x = x + inc_deg
        y = y + inc_deg
        a.record_affected(BBox(x, y, x + box_size, y + box_size))

    # Make sure our test math is right.
    end_x = start_x + deg
    assert round(x, 4) == round(end_x, 4)
    end_y = start_y + deg
    assert round(y, 4) == round(end_y, 4)
    box_east = end_x + box_size
    box_north = end_y + box_size

    b = a.get_affected_bbox()
    elapsed = time.time() - start_time
    assert elapsed < 1.0, "Recording and reporting on the affected bbox should take less than 1 second"
    assert b.west == start_x
    assert b.south == start_y
    assert round(b.east, 4) == round(box_east, 4)
    assert round(b.north, 4) == round(box_north, 4)

    tiles = a.get_affected_tiles(max_zoom=6, min_zoom=2)
    elapsed = time.time() - start_time
    assert elapsed < 1.0, "Reporting on affected tiles should take less than 1 seconds"

    assert len(tiles_at_zoom(tiles, 2)) == 1
    assert len(tiles_at_zoom(tiles, 3)) == 2
    assert len(tiles_at_zoom(tiles, 4)) == 2
    assert len(tiles_at_zoom(tiles, 5)) == 6
    assert len(tiles_at_zoom(tiles, 6)) == 12

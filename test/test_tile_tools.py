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

def test_bbox_from_coords():
    a = AffectedArea()
    coords = [
        (43.9493, -73.2548), # SW corner
        (43.997, -73.0), # middle, east
        (43.95, -73.10), # middle
        (44.0461, -73.20), # north, middle.
    ]
    a.record_affected(BBox.from_coords(coords))

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

def test_bbox_from_coords_performance():
    coords = [
        (43.9493, -73.2548), # SW corner
        (43.997, -73.0), # middle, east
        (43.95, -73.10), # middle
        (44.0461, -73.20), # north, middle.
    ]
    for i in range(0, 10000):
        coords.append((43.95, -73.10))
    start_time = time.time()
    bbox = BBox.from_coords(coords)
    elapsed = time.time() - start_time
    assert elapsed < 0.1, "Creating a 10,000 coord bbox should take less than 0.1 seconds"

def test_bbox_round_trip_through_geojson():
    coords = [
        (43.9493, -73.2548), # SW corner
        (43.997, -73.0), # middle, east
        (43.95, -73.10), # middle
        (44.0461, -73.20), # north, middle.
    ]
    bbox = BBox.from_coords(coords)
    geojson = bbox.as_geojson_string()

    new_bbox = BBox.from_geojson_string(geojson)
    assert new_bbox.west == -73.2548, "West should be equal"
    assert new_bbox.south == 43.9493, "South should be equal"
    assert new_bbox.east == -73.0, "East should be equal"
    assert new_bbox.north == 44.0461, "North should be equal"

    new_geojson = new_bbox.as_geojson_string()
    assert geojson == new_geojson

def test_bbox_round_trip_through_geojson_fiji():
    bbox = BBox(177.0, -20.0, -178.0, -16.0)
    geojson = bbox.as_geojson_string()

    new_bbox = BBox.from_geojson_string(geojson)
    assert new_bbox.west == 177.0, "West should be equal"
    assert new_bbox.south == -20.0, "South should be equal"
    assert new_bbox.east == -178.0, "East should be equal"
    assert new_bbox.north == -16.0, "North should be equal"

    new_geojson = new_bbox.as_geojson_string()
    assert geojson == new_geojson

def test_bbox_from_postgis_geojson_string():
    bbox = BBox.from_geojson_string('{"type":"Polygon","coordinates":[[[-73.426303,42.675246],[-73.426303,45.026259],[-71.46407,45.026259],[-71.46407,42.675246],[-73.426303,42.675246]]]}')
    assert bbox.west == -73.426303
    assert bbox.south == 42.675246
    assert bbox.east == -71.46407
    assert bbox.north == 45.026259

def test_lon_distance_west():
    # Both negative
    assert round(BBox.lon_distance_west(-73.3, -73.0), 1) == 359.7
    assert round(BBox.lon_distance_west(-73.0, -73.3), 1) == 0.3
    # Both positive
    assert round(BBox.lon_distance_west(73.3, 73.0), 1) == 0.3
    assert round(BBox.lon_distance_west(73.0, 73.3), 1) == 359.7
    # Across the meridan
    assert round(BBox.lon_distance_west(-1.5, 2.0), 1) == 356.5
    assert round(BBox.lon_distance_west(2.0, -1.5), 1) == 3.5
    # Across the meridan - farther
    assert round(BBox.lon_distance_west(-95.0, 25.0), 1) == 240.0
    assert round(BBox.lon_distance_west(25.0, -95.0), 1) == 120.0
    # 180°
    assert round(BBox.lon_distance_west(-95.0, 85.0), 1) == 180.0
    assert round(BBox.lon_distance_west(85.0, -95.0), 1) == 180.0
    # Across the antimeridan
    assert round(BBox.lon_distance_west(-178.5, 178.0), 1) == 3.5
    assert round(BBox.lon_distance_west(178.0, -178.5), 1) == 356.5
    # Across the antimeridan - farther
    assert round(BBox.lon_distance_west(110.0, -115.0), 1) == 225.0
    assert round(BBox.lon_distance_west(-115.0, 110.0), 1) == 135.0

def test_lon_distance_east():
    # Both negative
    assert round(BBox.lon_distance_east(-73.3, -73.0), 1) == 0.3
    assert round(BBox.lon_distance_east(-73.0, -73.3), 1) == 359.7
    # Both positive
    assert round(BBox.lon_distance_east(73.3, 73.0), 1) == 359.7
    assert round(BBox.lon_distance_east(73.0, 73.3), 1) == 0.3
    # Across the meridan
    assert round(BBox.lon_distance_east(-1.5, 2.0), 1) == 3.5
    assert round(BBox.lon_distance_east(2.0, -1.5), 1) == 356.5
    # Across the meridan - farther
    assert round(BBox.lon_distance_east(-95.0, 25.0), 1) == 120.0
    assert round(BBox.lon_distance_east(25.0, -95.0), 1) == 240.0
    # 180°
    assert round(BBox.lon_distance_east(-95.0, 85.0), 1) == 180.0
    assert round(BBox.lon_distance_east(85.0, -95.0), 1) == 180.0
    # Across the antimeridan
    assert round(BBox.lon_distance_east(-178.5, 178.0), 1) == 356.5
    assert round(BBox.lon_distance_east(178.0, -178.5), 1) == 3.5
    # Across the antimeridan - farther
    assert round(BBox.lon_distance_east(110.0, -115.0), 1) == 135.0
    assert round(BBox.lon_distance_east(-115.0, 110.0), 1) == 225.0

def test_min_lon_distance():
    # Both negative
    assert round(BBox.min_lon_distance(-73.3, -73.0), 1) == 0.3
    assert round(BBox.min_lon_distance(-73.0, -73.3), 1) == 0.3
    # Both positive
    assert round(BBox.min_lon_distance(73.3, 73.0), 1) == 0.3
    assert round(BBox.min_lon_distance(73.0, 73.3), 1) == 0.3
    # Across the meridan
    assert round(BBox.min_lon_distance(-1.5, 2.0), 1) == 3.5
    assert round(BBox.min_lon_distance(2.0, -1.5), 1) == 3.5
    # Across the meridan - farther
    assert round(BBox.min_lon_distance(-95.0, 25.0), 1) == 120.0
    assert round(BBox.min_lon_distance(-25.0, 95.0), 1) == 120.0
    # 180°
    assert round(BBox.min_lon_distance(-95.0, 85.0), 1) == 180.0
    assert round(BBox.min_lon_distance(-85.0, 95.0), 1) == 180.0
    # Across the antimeridan
    assert round(BBox.min_lon_distance(-178.5, 178.0), 1) == 3.5
    assert round(BBox.min_lon_distance(178.0, -178.5), 1) == 3.5
    # Across the antimeridan - farther
    assert round(BBox.min_lon_distance(110.0, -115.0), 1) == 135.0
    assert round(BBox.min_lon_distance(-115.0, 110.0), 1) == 135.0

def test_bbox_russia():
    # Start with two coords on either side of the antimeridan on the Bearing Straight.
    bbox = BBox.from_coords([(63.7, -167.3)])
    bbox = bbox.union(BBox.from_coords([(69.2, 173.6)]))
    assert bbox.west == 173.6
    assert bbox.south == 63.7
    assert bbox.east == -167.3
    assert bbox.north == 69.2

    # Add a far western point in Europe.
    bbox = bbox.union(BBox.from_coords([(59.8, 26.0)]))
    assert bbox.west == 26.0
    assert bbox.south == 59.8
    assert bbox.east == -167.3
    assert bbox.north == 69.2

    # Add the embassy in London. We should continue to wrap to the west.
    bbox = bbox.union(BBox.from_coords([(51.5, -0.1)]))
    assert bbox.west == -0.1
    assert bbox.south == 51.5
    assert bbox.east == -167.3
    assert bbox.north == 69.2

    # Add the embassy in Washington. We should continue to wrap to the west.
    # The BBox is now wrapping more than halfway around the world, but includes
    # all previous bboxes. Our eastern edge hasn't gotten confused.
    bbox = bbox.union(BBox.from_coords([(38.9, -77.0)]))
    assert bbox.west == -77.0
    assert bbox.south == 38.9
    assert bbox.east == -167.3
    assert bbox.north == 69.2

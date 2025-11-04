"""
Simple test script to verify stereopair functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stereopair import (
    StereoGenerator,
    GoogleImageryProvider,
    ESRIImageryProvider,
)


def test_imagery_providers():
    """Test imagery provider initialization."""
    print("Testing imagery providers...")

    google = GoogleImageryProvider()
    assert google is not None, "GoogleImageryProvider failed to initialize"

    esri = ESRIImageryProvider()
    assert esri is not None, "ESRIImageryProvider failed to initialize"

    print("✓ Imagery providers initialized successfully")


def test_stereo_generator():
    """Test stereo generator initialization."""
    print("Testing stereo generator...")

    imagery_provider = GoogleImageryProvider()
    generator = StereoGenerator(imagery_provider=imagery_provider)

    assert generator is not None, "StereoGenerator failed to initialize"
    assert generator.imagery_provider is not None, "Imagery provider not set"

    print("✓ Stereo generator initialized successfully")


def test_tile_conversion():
    """Test lat/lon to tile coordinate conversion."""
    print("Testing coordinate conversion...")

    from stereopair.imagery import ImageryProvider

    # Test conversion for a known location
    lat, lon, zoom = 36.1069, -112.1129, 17

    x, y = ImageryProvider.latlon_to_tile(lat, lon, zoom)
    assert isinstance(x, int), "Tile x coordinate should be integer"
    assert isinstance(y, int), "Tile y coordinate should be integer"

    # Test reverse conversion
    lat_back, lon_back = ImageryProvider.tile_to_latlon(x, y, zoom)
    assert abs(lat_back - lat) < 0.1, "Latitude conversion error too large"
    assert abs(lon_back - lon) < 0.1, "Longitude conversion error too large"

    print(f"✓ Coordinate conversion working (tile {x}, {y} at zoom {zoom})")


def test_stereo_geometry_calculation():
    """Test stereo geometry calculation."""
    print("Testing stereo geometry calculation...")

    imagery_provider = GoogleImageryProvider()
    generator = StereoGenerator(imagery_provider=imagery_provider)

    metadata = generator._calculate_stereo_geometry(
        center_lat=36.1069,
        center_lon=-112.1129,
        zoom=17,
        base_height_ratio=0.6,
        convergence_angle=10.0,
    )

    assert "center" in metadata, "Center not in metadata"
    assert "left_camera" in metadata, "Left camera not in metadata"
    assert "right_camera" in metadata, "Right camera not in metadata"
    assert "geometry" in metadata, "Geometry not in metadata"

    assert metadata["geometry"]["baseline_meters"] > 0, "Baseline should be positive"
    assert (
        metadata["geometry"]["flying_height_meters"] > 0
    ), "Flying height should be positive"

    print("✓ Stereo geometry calculation working")
    print(f"  Baseline: {metadata['geometry']['baseline_meters']:.2f} meters")
    print(f"  Flying height: {metadata['geometry']['flying_height_meters']:.2f} meters")


def test_anaglyph_creation():
    """Test anaglyph creation from dummy images."""
    print("Testing anaglyph creation...")

    from PIL import Image
    import numpy as np

    # Create dummy stereo pair
    left_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    right_array = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    left_image = Image.fromarray(left_array)
    right_image = Image.fromarray(right_array)

    imagery_provider = GoogleImageryProvider()
    generator = StereoGenerator(imagery_provider=imagery_provider)

    anaglyph = generator.create_anaglyph(left_image, right_image, method="red-cyan")

    assert anaglyph is not None, "Anaglyph creation failed"
    assert anaglyph.size == left_image.size, "Anaglyph size mismatch"

    print("✓ Anaglyph creation working")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STEREOPAIR LIBRARY - BASIC TESTS")
    print("=" * 60 + "\n")

    try:
        test_imagery_providers()
        test_stereo_generator()
        test_tile_conversion()
        test_stereo_geometry_calculation()
        test_anaglyph_creation()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60 + "\n")

        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

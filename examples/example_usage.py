"""
Example usage of the stereopair library.

This script demonstrates how to generate stereo image pairs from satellite imagery.
"""

from stereopair import (
    StereoGenerator,
    GoogleImageryProvider,
    ESRIImageryProvider,
    BingImageryProvider,
    CustomDEMProvider,
)
import sys


def example_basic_stereo_pair():
    """Generate a basic stereo pair using Google imagery."""
    print("=" * 60)
    print("Example 1: Basic Stereo Pair Generation")
    print("=" * 60)

    # Initialize imagery provider (Google by default)
    imagery_provider = GoogleImageryProvider()

    # Create stereo generator
    generator = StereoGenerator(imagery_provider=imagery_provider)

    # Define location (example: Grand Canyon)
    center_lat = 36.1069
    center_lon = -112.1129

    print(f"\nGenerating stereo pair for location:")
    print(f"  Latitude: {center_lat}")
    print(f"  Longitude: {center_lon}")

    # Generate stereo pair
    left_image, right_image, metadata = generator.generate_stereo_pair(
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=17,
        base_height_ratio=0.6,
        convergence_angle=10.0,
        image_size=(800, 800),
    )

    if left_image and right_image:
        # Export the stereo pair
        generator.export_stereo_pair(
            left_image=left_image,
            right_image=right_image,
            output_prefix="example_basic",
            metadata=metadata,
            export_anaglyph=True,
        )
        print("\n✓ Stereo pair generated successfully!")
        print(f"\nStereo Geometry:")
        print(f"  Baseline: {metadata['geometry']['baseline_meters']:.2f} meters")
        print(f"  Flying Height: {metadata['geometry']['flying_height_meters']:.2f} meters")
        print(f"  Base/Height Ratio: {metadata['geometry']['base_height_ratio']:.2f}")
        print(f"  Convergence Angle: {metadata['geometry']['convergence_angle_degrees']:.2f}°")
    else:
        print("\n✗ Failed to generate stereo pair")


def example_with_esri_imagery():
    """Generate a stereo pair using ESRI World Imagery."""
    print("\n" + "=" * 60)
    print("Example 2: Using ESRI World Imagery")
    print("=" * 60)

    # Initialize ESRI imagery provider
    imagery_provider = ESRIImageryProvider()

    # Create stereo generator
    generator = StereoGenerator(imagery_provider=imagery_provider)

    # Define location (example: Mount Everest)
    center_lat = 27.9881
    center_lon = 86.9250

    print(f"\nGenerating stereo pair for location:")
    print(f"  Latitude: {center_lat}")
    print(f"  Longitude: {center_lon}")

    # Generate stereo pair with different parameters
    left_image, right_image, metadata = generator.generate_stereo_pair(
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=16,
        base_height_ratio=0.7,  # Higher for more pronounced 3D effect
        convergence_angle=12.0,
        image_size=(1024, 1024),
    )

    if left_image and right_image:
        generator.export_stereo_pair(
            left_image=left_image,
            right_image=right_image,
            output_prefix="example_esri",
            metadata=metadata,
            export_anaglyph=True,
        )
        print("\n✓ Stereo pair generated successfully with ESRI imagery!")
    else:
        print("\n✗ Failed to generate stereo pair")


def example_with_custom_dem():
    """Generate a stereo pair with custom DEM (requires DEM file)."""
    print("\n" + "=" * 60)
    print("Example 3: Using Custom DEM (Optional)")
    print("=" * 60)

    import os

    # Check if a DEM file is provided
    dem_file = "path/to/your/dem.tif"  # Update this path

    if not os.path.exists(dem_file):
        print(f"\nSkipping: DEM file not found at {dem_file}")
        print("To use this example, provide a valid GeoTIFF DEM file path")
        return

    # Initialize imagery and DEM providers
    imagery_provider = GoogleImageryProvider()
    dem_provider = CustomDEMProvider(dem_path=dem_file)

    # Create stereo generator with DEM
    generator = StereoGenerator(
        imagery_provider=imagery_provider, dem_provider=dem_provider
    )

    # Define location
    center_lat = 40.7589  # Example: New York City
    center_lon = -73.9851

    print(f"\nGenerating terrain-corrected stereo pair for location:")
    print(f"  Latitude: {center_lat}")
    print(f"  Longitude: {center_lon}")

    # Generate stereo pair
    left_image, right_image, metadata = generator.generate_stereo_pair(
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=17,
        base_height_ratio=0.6,
        convergence_angle=10.0,
    )

    if left_image and right_image:
        generator.export_stereo_pair(
            left_image=left_image,
            right_image=right_image,
            output_prefix="example_dem",
            metadata=metadata,
            export_anaglyph=True,
        )
        print("\n✓ Terrain-corrected stereo pair generated successfully!")
    else:
        print("\n✗ Failed to generate stereo pair")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("STEREOPAIR LIBRARY - USAGE EXAMPLES")
    print("=" * 60)

    try:
        # Run examples
        example_basic_stereo_pair()
        example_with_esri_imagery()
        example_with_custom_dem()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - example_basic_left.png, example_basic_right.png, example_basic_anaglyph.png")
        print("  - example_esri_left.png, example_esri_right.png, example_esri_anaglyph.png")
        print("  - Metadata JSON files with camera parameters")
        print("\nView the anaglyph images with red-cyan 3D glasses for 3D effect!")

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

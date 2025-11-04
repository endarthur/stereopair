"""
Offline demo of stereopair library functionality.

This demo creates synthetic images to demonstrate the library features
without requiring network access.
"""

from stereopair import StereoGenerator, GoogleImageryProvider
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def create_synthetic_imagery_provider():
    """Create a synthetic imagery provider that doesn't require network access."""

    class SyntheticImageryProvider(GoogleImageryProvider):
        """Synthetic imagery provider for testing without network."""

        def get_tile(self, lat, lon, zoom):
            """Generate a synthetic tile image."""
            # Create a 256x256 image with a pattern
            img = Image.new("RGB", (256, 256), color=(100, 150, 200))
            draw = ImageDraw.Draw(img)

            # Draw grid
            for i in range(0, 256, 32):
                draw.line([(i, 0), (i, 256)], fill=(150, 150, 150), width=1)
                draw.line([(0, i), (256, i)], fill=(150, 150, 150), width=1)

            # Draw some features
            draw.ellipse([64, 64, 192, 192], fill=(80, 120, 80), outline=(50, 90, 50))
            draw.rectangle([100, 100, 156, 156], fill=(200, 200, 200))

            # Add text with coordinates
            try:
                draw.text(
                    (10, 10),
                    f"Lat:{lat:.4f}\nLon:{lon:.4f}\nZ:{zoom}",
                    fill=(255, 255, 255),
                )
            except:
                # Font may not be available, skip text
                pass

            return img

    return SyntheticImageryProvider()


def main():
    """Run the offline demo."""
    print("\n" + "=" * 70)
    print("STEREOPAIR LIBRARY - OFFLINE DEMO")
    print("=" * 70)

    # Create synthetic imagery provider
    print("\n1. Creating synthetic imagery provider...")
    imagery_provider = create_synthetic_imagery_provider()
    print("   ✓ Synthetic provider created")

    # Create stereo generator
    print("\n2. Initializing stereo generator...")
    generator = StereoGenerator(imagery_provider=imagery_provider)
    print("   ✓ Generator initialized")

    # Define location (Grand Canyon coordinates)
    center_lat = 36.1069
    center_lon = -112.1129

    print(f"\n3. Generating stereo pair for location:")
    print(f"   Center: {center_lat}°N, {center_lon}°W")

    # Generate stereo pair
    print("\n4. Computing stereo geometry...")
    left_image, right_image, metadata = generator.generate_stereo_pair(
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=17,
        base_height_ratio=0.6,
        convergence_angle=10.0,
        image_size=(512, 512),
    )

    if left_image and right_image:
        print("   ✓ Stereo pair generated successfully!")

        # Display stereo geometry
        print("\n5. Stereo Geometry Parameters:")
        print(f"   Baseline: {metadata['geometry']['baseline_meters']:.2f} meters")
        print(
            f"   Flying Height: {metadata['geometry']['flying_height_meters']:.2f} meters"
        )
        print(f"   Base/Height Ratio: {metadata['geometry']['base_height_ratio']:.2f}")
        print(
            f"   Convergence Angle: {metadata['geometry']['convergence_angle_degrees']:.2f}°"
        )
        print(f"   Ground Sampling Distance: {metadata['geometry']['gsd_meters']:.4f} meters/pixel")

        # Display camera positions
        print("\n6. Camera Positions:")
        print(f"   Left Camera: {metadata['left_camera']['lat']:.6f}°, {metadata['left_camera']['lon']:.6f}°")
        print(f"   Right Camera: {metadata['right_camera']['lat']:.6f}°, {metadata['right_camera']['lon']:.6f}°")

        # Export stereo pair
        print("\n7. Exporting stereo pair images...")
        generator.export_stereo_pair(
            left_image=left_image,
            right_image=right_image,
            output_prefix="demo_stereo",
            metadata=metadata,
            export_anaglyph=True,
        )

        print("\n" + "=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - demo_stereo_left.png      (Left stereo image)")
        print("  - demo_stereo_right.png     (Right stereo image)")
        print("  - demo_stereo_anaglyph.png  (Red-cyan anaglyph for 3D viewing)")
        print("  - demo_stereo_metadata.json (Camera parameters and geometry)")
        print(
            "\nNote: Use red-cyan 3D glasses to view the anaglyph image for 3D effect!"
        )
        print("=" * 70 + "\n")

    else:
        print("\n✗ Failed to generate stereo pair")


if __name__ == "__main__":
    main()

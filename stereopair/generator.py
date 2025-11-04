"""
Stereo pair generator - core functionality for creating stereo image pairs.
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional, Dict, Any
import math
from .imagery import ImageryProvider
from .dem import DEMProvider


class StereoGenerator:
    """
    Generator for creating stereo image pairs from satellite imagery and DEM data.

    This class combines satellite imagery with elevation data to generate stereo
    pairs suitable for photogrammetric analysis and 3D reconstruction.
    """

    def __init__(
        self,
        imagery_provider: ImageryProvider,
        dem_provider: Optional[DEMProvider] = None,
    ):
        """
        Initialize the stereo generator.

        Args:
            imagery_provider: Provider for satellite imagery
            dem_provider: Provider for DEM data (optional, for terrain-corrected pairs)
        """
        self.imagery_provider = imagery_provider
        self.dem_provider = dem_provider

    def generate_stereo_pair(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int = 17,
        base_height_ratio: float = 0.6,
        convergence_angle: float = 10.0,
        image_size: Tuple[int, int] = (512, 512),
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image], Dict[str, Any]]:
        """
        Generate a stereo pair of images centered at the given location.

        Args:
            center_lat: Center latitude in decimal degrees
            center_lon: Center longitude in decimal degrees
            zoom: Zoom level for imagery (higher = more detail, typically 15-19)
            base_height_ratio: Ratio of baseline to flying height (0.5-0.8 typical)
                              Higher values give more pronounced 3D effect
            convergence_angle: Convergence angle in degrees (5-15 typical)
                              Angle between the two camera viewing directions
            image_size: Size of output images in pixels (width, height)

        Returns:
            Tuple of (left_image, right_image, metadata_dict)
            metadata includes camera parameters and geometry
        """
        # Get base imagery
        base_image = self.imagery_provider.get_tile(center_lat, center_lon, zoom)
        if base_image is None:
            return None, None, {}

        # Calculate stereo geometry
        metadata = self._calculate_stereo_geometry(
            center_lat, center_lon, zoom, base_height_ratio, convergence_angle
        )

        # Get left and right camera positions
        left_lat, left_lon = metadata["left_camera"]["lat"], metadata["left_camera"]["lon"]
        right_lat, right_lon = metadata["right_camera"]["lat"], metadata["right_camera"]["lon"]

        # Fetch images from left and right viewpoints
        left_image = self.imagery_provider.get_tile(left_lat, left_lon, zoom)
        right_image = self.imagery_provider.get_tile(right_lat, right_lon, zoom)

        # Apply perspective transformation if DEM is available
        if self.dem_provider is not None:
            left_image = self._apply_terrain_correction(
                left_image, left_lat, left_lon, center_lat, center_lon, zoom
            )
            right_image = self._apply_terrain_correction(
                right_image, right_lat, right_lon, center_lat, center_lon, zoom
            )

        # Resize to requested size
        if left_image:
            left_image = left_image.resize(image_size, Image.Resampling.LANCZOS)
        if right_image:
            right_image = right_image.resize(image_size, Image.Resampling.LANCZOS)

        return left_image, right_image, metadata

    def _calculate_stereo_geometry(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int,
        base_height_ratio: float,
        convergence_angle: float,
    ) -> Dict[str, Any]:
        """
        Calculate stereo camera geometry.

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            zoom: Zoom level
            base_height_ratio: Base to height ratio
            convergence_angle: Convergence angle in degrees

        Returns:
            Dictionary with camera parameters and positions
        """
        # Estimate ground sampling distance (GSD) based on zoom level
        # At zoom 17, GSD is approximately 1.2 meters at equator
        gsd_meters = (40075017 * math.cos(math.radians(center_lat))) / (2 ** (zoom + 8))

        # Estimate flying height (assuming typical aerial photography)
        # For satellite imagery, this is more of a virtual camera height
        flying_height = 5000  # meters, typical for aerial stereo

        # Calculate baseline
        baseline = flying_height * base_height_ratio

        # Calculate camera positions
        # Place cameras along east-west axis for simplicity
        convergence_rad = math.radians(convergence_angle)

        # Offset in degrees (approximate)
        meters_per_degree = 111000 * math.cos(math.radians(center_lat))
        offset_degrees = (baseline / 2) / meters_per_degree

        left_lon = center_lon - offset_degrees
        right_lon = center_lon + offset_degrees

        # Apply convergence by shifting the view centers
        convergence_offset = flying_height * math.tan(convergence_rad / 2)
        convergence_offset_deg = convergence_offset / meters_per_degree

        metadata = {
            "center": {"lat": center_lat, "lon": center_lon},
            "left_camera": {
                "lat": center_lat,
                "lon": left_lon,
                "view_center_lon": center_lon - convergence_offset_deg / 2,
            },
            "right_camera": {
                "lat": center_lat,
                "lon": right_lon,
                "view_center_lon": center_lon + convergence_offset_deg / 2,
            },
            "geometry": {
                "baseline_meters": baseline,
                "flying_height_meters": flying_height,
                "base_height_ratio": base_height_ratio,
                "convergence_angle_degrees": convergence_angle,
                "gsd_meters": gsd_meters,
            },
            "zoom": zoom,
        }

        return metadata

    def _apply_terrain_correction(
        self,
        image: Optional[Image.Image],
        camera_lat: float,
        camera_lon: float,
        target_lat: float,
        target_lon: float,
        zoom: int,
    ) -> Optional[Image.Image]:
        """
        Apply terrain correction to an image using DEM data.

        This is a simplified version - a full implementation would require
        orthorectification and perspective transformation based on the DEM.

        Args:
            image: Input image
            camera_lat: Camera position latitude
            camera_lon: Camera position longitude
            target_lat: Target (looking at) latitude
            target_lon: Target (looking at) longitude
            zoom: Zoom level

        Returns:
            Corrected image or original if correction fails
        """
        if image is None or self.dem_provider is None:
            return image

        try:
            # Get elevation at target point
            elevation = self.dem_provider.get_elevation_at_point(target_lat, target_lon)

            if elevation is not None:
                # In a full implementation, this would apply perspective transformation
                # based on terrain elevation. For now, we return the original image.
                # This is a placeholder for more advanced orthorectification.
                pass

            return image
        except Exception as e:
            print(f"Warning: Terrain correction failed: {e}")
            return image

    def create_anaglyph(
        self,
        left_image: Image.Image,
        right_image: Image.Image,
        method: str = "red-cyan",
    ) -> Image.Image:
        """
        Create an anaglyph 3D image from a stereo pair.

        Args:
            left_image: Left stereo image
            right_image: Right stereo image
            method: Anaglyph method ('red-cyan', 'red-green', 'red-blue')

        Returns:
            Anaglyph image
        """
        # Convert to RGB if needed
        if left_image.mode != "RGB":
            left_image = left_image.convert("RGB")
        if right_image.mode != "RGB":
            right_image = right_image.convert("RGB")

        # Ensure same size
        if left_image.size != right_image.size:
            right_image = right_image.resize(left_image.size, Image.Resampling.LANCZOS)

        # Convert to numpy arrays
        left_array = np.array(left_image)
        right_array = np.array(right_image)

        # Create anaglyph based on method
        anaglyph = np.zeros_like(left_array)

        if method == "red-cyan":
            anaglyph[:, :, 0] = left_array[:, :, 0]  # Red from left
            anaglyph[:, :, 1] = right_array[:, :, 1]  # Green from right
            anaglyph[:, :, 2] = right_array[:, :, 2]  # Blue from right
        elif method == "red-green":
            anaglyph[:, :, 0] = left_array[:, :, 0]  # Red from left
            anaglyph[:, :, 1] = right_array[:, :, 1]  # Green from right
        elif method == "red-blue":
            anaglyph[:, :, 0] = left_array[:, :, 0]  # Red from left
            anaglyph[:, :, 2] = right_array[:, :, 2]  # Blue from right

        return Image.fromarray(anaglyph)

    def export_stereo_pair(
        self,
        left_image: Image.Image,
        right_image: Image.Image,
        output_prefix: str,
        metadata: Optional[Dict[str, Any]] = None,
        export_anaglyph: bool = True,
    ):
        """
        Export stereo pair images to files.

        Args:
            left_image: Left stereo image
            right_image: Right stereo image
            output_prefix: Prefix for output filenames
            metadata: Optional metadata to save
            export_anaglyph: Whether to also export anaglyph image
        """
        import json

        # Save left and right images
        left_image.save(f"{output_prefix}_left.png")
        right_image.save(f"{output_prefix}_right.png")
        print(f"Saved stereo pair: {output_prefix}_left.png and {output_prefix}_right.png")

        # Save anaglyph if requested
        if export_anaglyph:
            anaglyph = self.create_anaglyph(left_image, right_image)
            anaglyph.save(f"{output_prefix}_anaglyph.png")
            print(f"Saved anaglyph: {output_prefix}_anaglyph.png")

        # Save metadata if provided
        if metadata:
            with open(f"{output_prefix}_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            print(f"Saved metadata: {output_prefix}_metadata.json")

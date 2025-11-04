"""
Stereo pair generator - core functionality for creating stereo image pairs.
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional, Dict, Any, Union
import math
from .imagery import ImageryProvider
from .dem import DEMProvider


# Constants for stereo geometry calculations
EARTH_CIRCUMFERENCE_METERS = 40075017  # Earth's equatorial circumference in meters
METERS_PER_DEGREE_EQUATOR = 111000  # Approximate meters per degree at equator
DEFAULT_FLYING_HEIGHT_METERS = 5000  # Default virtual camera height for stereo calculations


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
        zoom: Optional[int] = None,
        scale: Optional[Union[int, float, str]] = None,
        base_height_ratio: float = 0.6,
        convergence_angle: float = 10.0,
        image_size: Optional[Union[Tuple[int, int], str]] = None,
        flying_height: float = 5000.0,
    ) -> Tuple[Optional[Image.Image], Optional[Image.Image], Dict[str, Any]]:
        """
        Generate a stereo pair of images centered at the given location.

        Args:
            center_lat: Center latitude in decimal degrees
            center_lon: Center longitude in decimal degrees
            zoom: Zoom level for imagery (0-20). If None, must provide scale.
            scale: Map scale as number (5000) or string ("1:5000"). Alternative to zoom.
            base_height_ratio: Ratio of baseline to flying height (0.5-0.8 typical)
                              Higher values give more pronounced 3D effect
            convergence_angle: Convergence angle in degrees (5-15 typical)
                              Angle between the two camera viewing directions
            image_size: Output image size as (width, height) in pixels, or standard size name
                       (e.g., "23x23_cm", "medium"). If None, defaults to (512, 512).
            flying_height: Flying height above ground in meters (default 5000m)

        Returns:
            Tuple of (left_image, right_image, metadata_dict)
            metadata includes camera parameters and stereo geometry
            
        Raises:
            ValueError: If neither zoom nor scale is provided, or both are provided
        """
        from .utils import parse_scale, scale_to_zoom_level, zoom_level_to_gsd, get_image_size_pixels
        
        # Validate inputs
        if zoom is None and scale is None:
            raise ValueError("Must provide either 'zoom' or 'scale' parameter")
        if zoom is not None and scale is not None:
            raise ValueError("Cannot provide both 'zoom' and 'scale' parameters")
        
        # Convert scale to zoom if needed
        if scale is not None:
            scale_value = parse_scale(scale)
            zoom = scale_to_zoom_level(scale_value, center_lat, flying_height)
        
        # Calculate GSD for this zoom level
        gsd = zoom_level_to_gsd(zoom, center_lat)
        
        # Determine image size
        if image_size is None:
            final_image_size = (512, 512)
        elif isinstance(image_size, str):
            # Standard photo size - calculate pixels from GSD
            final_image_size = get_image_size_pixels(image_size, gsd)
        else:
            final_image_size = image_size
        
        # Get base imagery
        base_image = self.imagery_provider.get_tile(center_lat, center_lon, zoom)
        if base_image is None:
            return None, None, {}

        # Calculate stereo geometry
        metadata = self._calculate_stereo_geometry(
            center_lat, center_lon, zoom, base_height_ratio, convergence_angle, flying_height
        )
        
        # Add scale information to metadata
        metadata["scale"] = {
            "gsd_meters": gsd,
            "flying_height_meters": flying_height,
        }
        if scale is not None:
            metadata["scale"]["map_scale"] = scale_value

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
            left_image = left_image.resize(final_image_size, Image.Resampling.LANCZOS)
        if right_image:
            right_image = right_image.resize(final_image_size, Image.Resampling.LANCZOS)

        return left_image, right_image, metadata

    def _calculate_stereo_geometry(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int,
        base_height_ratio: float,
        convergence_angle: float,
        flying_height: float = DEFAULT_FLYING_HEIGHT_METERS,
    ) -> Dict[str, Any]:
        """
        Calculate stereo camera geometry.

        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            zoom: Zoom level
            base_height_ratio: Base to height ratio
            convergence_angle: Convergence angle in degrees
            flying_height: Flying height in meters

        Returns:
            Dictionary with camera parameters and positions
        """
        # Estimate ground sampling distance (GSD) based on zoom level
        # At zoom 17, GSD is approximately 1.2 meters at equator
        gsd_meters = (EARTH_CIRCUMFERENCE_METERS * math.cos(math.radians(center_lat))) / (2 ** (zoom + 8))

        # Calculate baseline
        baseline = flying_height * base_height_ratio

        # Calculate camera positions
        # Place cameras along east-west axis for simplicity
        convergence_rad = math.radians(convergence_angle)

        # Offset in degrees (approximate)
        meters_per_degree = METERS_PER_DEGREE_EQUATOR * math.cos(math.radians(center_lat))
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

    def generate_aerial_survey(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        num_positions: int = 5,
        zoom: Optional[int] = None,
        scale: Optional[Union[int, float, str]] = None,
        base_height_ratio: float = 0.6,
        convergence_angle: float = 10.0,
        image_size: Optional[Union[Tuple[int, int], str]] = None,
        flying_height: float = 5000.0,
        overlap_percent: float = 60.0,
    ) -> list:
        """
        Generate a series of stereo pairs along a flight line (aerial survey).

        This simulates an aerial photogrammetric survey by creating multiple
        stereo pairs along a linear path from start to end position.

        Args:
            start_lat: Starting latitude in decimal degrees
            start_lon: Starting longitude in decimal degrees
            end_lat: Ending latitude in decimal degrees
            end_lon: Ending longitude in decimal degrees
            num_positions: Number of stereo pair positions along the flight line
            zoom: Zoom level for imagery (0-20). If None, must provide scale.
            scale: Map scale as number (5000) or string ("1:5000"). Alternative to zoom.
            base_height_ratio: Ratio of baseline to flying height (0.5-0.8 typical)
            convergence_angle: Convergence angle in degrees (5-15 typical)
            image_size: Output image size as (width, height) in pixels, or standard size name.
                       If None, defaults to (512, 512).
            flying_height: Flying height above ground in meters (default 5000m)
            overlap_percent: Percentage of overlap between consecutive positions (typical 60-80%)

        Returns:
            List of tuples, each containing (left_image, right_image, metadata_dict, position_index)
        """
        survey_results = []

        # Calculate positions along the flight line
        for i in range(num_positions):
            # Linear interpolation between start and end
            t = i / max(1, num_positions - 1) if num_positions > 1 else 0
            current_lat = start_lat + t * (end_lat - start_lat)
            current_lon = start_lon + t * (end_lon - start_lon)

            print(f"Generating stereo pair {i+1}/{num_positions} at ({current_lat:.6f}, {current_lon:.6f})...")

            # Generate stereo pair for this position
            left, right, metadata = self.generate_stereo_pair(
                center_lat=current_lat,
                center_lon=current_lon,
                zoom=zoom,
                scale=scale,
                base_height_ratio=base_height_ratio,
                convergence_angle=convergence_angle,
                image_size=image_size,
                flying_height=flying_height,
            )

            if left is not None and right is not None:
                # Add position index to metadata
                metadata["survey_position"] = {
                    "index": i,
                    "total_positions": num_positions,
                    "overlap_percent": overlap_percent,
                }
                survey_results.append((left, right, metadata, i))
            else:
                print(f"Warning: Failed to generate stereo pair for position {i+1}")

        return survey_results

    def export_aerial_survey(
        self,
        survey_results: list,
        output_dir: str,
        base_name: str = "survey",
        export_anaglyph: bool = True,
    ):
        """
        Export aerial survey results to files.

        Args:
            survey_results: List of survey results from generate_aerial_survey()
            output_dir: Directory to save output files
            base_name: Base name for output files
            export_anaglyph: Whether to also export anaglyph images
        """
        import os
        import json

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Export each stereo pair
        for left, right, metadata, position in survey_results:
            prefix = os.path.join(output_dir, f"{base_name}_pos{position:03d}")
            self.export_stereo_pair(left, right, prefix, metadata, export_anaglyph)

        # Create survey overview metadata
        survey_metadata = {
            "survey_name": base_name,
            "num_positions": len(survey_results),
            "positions": [],
        }

        for _, _, metadata, position in survey_results:
            survey_metadata["positions"].append({
                "index": position,
                "center": metadata["center"],
                "geometry": metadata["geometry"],
            })

        # Save survey overview
        overview_path = os.path.join(output_dir, f"{base_name}_survey_overview.json")
        with open(overview_path, "w") as f:
            json.dump(survey_metadata, f, indent=2)
        print(f"\nSaved survey overview: {overview_path}")

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

"""
Utility functions for scale conversions and photogrammetric calculations.
"""

import math
from typing import Union, Tuple


def parse_scale(scale: Union[int, float, str]) -> float:
    """
    Parse scale input to a numeric scale denominator.
    
    Args:
        scale: Scale as integer (5000), float (5000.0), or string ("1:5000" or "5000")
    
    Returns:
        Scale denominator as float (e.g., 5000.0)
    
    Examples:
        >>> parse_scale(5000)
        5000.0
        >>> parse_scale("1:5000")
        5000.0
        >>> parse_scale("5000")
        5000.0
    """
    if isinstance(scale, (int, float)):
        return float(scale)
    
    if isinstance(scale, str):
        scale = scale.strip()
        # Handle "1:5000" format
        if ':' in scale:
            parts = scale.split(':')
            if len(parts) == 2:
                numerator = float(parts[0])
                denominator = float(parts[1])
                if numerator != 1.0:
                    raise ValueError(f"Scale numerator must be 1, got {numerator}")
                return denominator
        # Handle plain number as string "5000"
        return float(scale)
    
    raise ValueError(f"Invalid scale format: {scale}")


def scale_to_gsd(scale: float, flying_height: float, focal_length: float = 0.153) -> float:
    """
    Convert photo scale to ground sampling distance (GSD).
    
    For aerial photography: scale = focal_length / flying_height
    However, this is the photo scale, not the digital GSD.
    
    For digital imagery, we need to consider the sensor and output format.
    A simpler approach: GSD ≈ (physical_pixel_size * scale) / focal_length_mm
    
    But for tile-based imagery, it's better to use the zoom-level based calculation.
    This function provides a rough estimate for reference.
    
    Args:
        scale: Map scale denominator (e.g., 5000 for 1:5000)
        flying_height: Flying height above ground in meters
        focal_length: Camera focal length in meters (default 153mm = 0.153m)
    
    Returns:
        Ground sampling distance in meters per pixel (rough estimate)
    """
    # For aerial photos at 1:S scale, the photo scale S relates to ground distance
    # Photo distance 1cm represents S cm on ground
    # For a 23cm x 23cm photo at 1:5000, it covers 23cm * 5000 = 1150m on ground
    # With typical 9000x9000 pixel scan, GSD = 1150m / 9000 = 0.128 m/pixel
    
    # Simplified: assume standard 23cm photo scanned at ~100 pixels/cm
    # Photo covers: 0.23m * scale on ground
    # Pixels: 0.23m * 100 = 2300 pixels
    # GSD = (0.23 * scale) / 2300
    
    photo_size_m = 0.23  # Standard 23cm photo
    scan_resolution_px = 2300  # Typical scan resolution
    ground_coverage_m = photo_size_m * scale
    gsd = ground_coverage_m / scan_resolution_px
    
    return gsd


def gsd_to_zoom_level(gsd: float, latitude: float) -> int:
    """
    Convert GSD to approximate tile zoom level.
    
    Tile zoom levels provide GSD that varies with latitude:
    At equator, zoom Z gives GSD ≈ 40075017 / (256 * 2^Z) meters/pixel
    
    Args:
        gsd: Ground sampling distance in meters per pixel
        latitude: Latitude in decimal degrees (affects GSD calculation)
    
    Returns:
        Approximate zoom level (clamped to 0-20)
    """
    # Earth circumference at equator in meters
    earth_circumference = 40075017
    
    # Adjust for latitude
    earth_circ_at_lat = earth_circumference * math.cos(math.radians(latitude))
    
    # At zoom level Z, one tile (256 pixels) covers:
    # tile_width = earth_circ_at_lat / (2^Z)
    # So GSD at zoom Z = tile_width / 256 = earth_circ_at_lat / (256 * 2^Z)
    # 
    # Solving for Z: 2^Z = earth_circ_at_lat / (256 * gsd)
    # Z = log2(earth_circ_at_lat / (256 * gsd))
    
    if gsd <= 0:
        return 20  # Maximum zoom
    
    zoom = math.log2(earth_circ_at_lat / (256 * gsd))
    
    # Clamp to valid range
    return max(0, min(20, int(round(zoom))))


def scale_to_zoom_level(scale: float, latitude: float, flying_height: float = 5000.0) -> int:
    """
    Convert map scale to approximate tile zoom level.
    
    Args:
        scale: Map scale denominator (e.g., 5000 for 1:5000)
        latitude: Latitude in decimal degrees
        flying_height: Flying height in meters (default 5000m)
    
    Returns:
        Approximate zoom level
    """
    gsd = scale_to_gsd(scale, flying_height)
    return gsd_to_zoom_level(gsd, latitude)


def zoom_level_to_gsd(zoom: int, latitude: float) -> float:
    """
    Convert tile zoom level to GSD at given latitude.
    
    Args:
        zoom: Tile zoom level (0-20)
        latitude: Latitude in decimal degrees
    
    Returns:
        GSD in meters per pixel
    """
    earth_circumference = 40075017
    earth_circ_at_lat = earth_circumference * math.cos(math.radians(latitude))
    gsd = earth_circ_at_lat / (256 * (2 ** zoom))
    return gsd


# Standard photo ground coverage (width, height) in meters
# These represent the ground area covered by typical aerial photos at various scales
STANDARD_PHOTO_SIZES = {
    "9x9_inch_1_5000": (1150, 1150),    # 9x9" photo at 1:5000 covers ~1150m x 1150m
    "23x23_cm_1_5000": (1150, 1150),    # 23x23cm photo at 1:5000
    "23x23_cm_1_10000": (2300, 2300),   # 23x23cm photo at 1:10000
    "small": (500, 500),                # Small coverage (500m x 500m)
    "medium": (1000, 1000),             # Medium coverage (1km x 1km)
    "large": (2000, 2000),              # Large coverage (2km x 2km)
    "xlarge": (5000, 5000),             # Extra large coverage (5km x 5km)
}


def get_image_size_pixels(
    photo_size: Union[str, Tuple[float, float]],
    gsd: float
) -> Tuple[int, int]:
    """
    Calculate image size in pixels from ground coverage and GSD.
    
    Args:
        photo_size: Photo size as standard name (e.g., "medium") or 
                   tuple of (width, height) in meters (ground coverage)
        gsd: Ground sampling distance in meters per pixel
    
    Returns:
        Image size in pixels (width, height)
    """
    if isinstance(photo_size, str):
        if photo_size not in STANDARD_PHOTO_SIZES:
            raise ValueError(
                f"Unknown photo size '{photo_size}'. "
                f"Available: {list(STANDARD_PHOTO_SIZES.keys())}"
            )
        size_m = STANDARD_PHOTO_SIZES[photo_size]
    else:
        size_m = photo_size
    
    # Convert ground coverage to pixels using GSD
    width_px = int(size_m[0] / gsd)
    height_px = int(size_m[1] / gsd)
    
    return (width_px, height_px)

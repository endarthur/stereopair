"""
Imagery providers for different satellite imagery sources.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
import requests
from io import BytesIO
from PIL import Image
import numpy as np


class ImageryProvider(ABC):
    """Abstract base class for imagery providers."""

    @abstractmethod
    def get_tile(self, lat: float, lon: float, zoom: int) -> Optional[Image.Image]:
        """
        Get a satellite imagery tile at the specified location and zoom level.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            zoom: Zoom level (typically 0-20)

        Returns:
            PIL Image object or None if unavailable
        """
        pass

    @staticmethod
    def latlon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """
        Convert latitude/longitude to tile coordinates.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            zoom: Zoom level

        Returns:
            Tuple of (x, y) tile coordinates
        """
        import math

        lat_rad = math.radians(lat)
        n = 2.0**zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return (x, y)

    @staticmethod
    def tile_to_latlon(x: int, y: int, zoom: int) -> Tuple[float, float]:
        """
        Convert tile coordinates to latitude/longitude.

        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            zoom: Zoom level

        Returns:
            Tuple of (lat, lon) in decimal degrees
        """
        import math

        n = 2.0**zoom
        lon = x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
        lat = math.degrees(lat_rad)
        return (lat, lon)


class GoogleImageryProvider(ImageryProvider):
    """Provider for Google Satellite imagery."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google imagery provider.

        Args:
            api_key: Optional Google Maps API key (required for production use)
        """
        self.api_key = api_key
        self.base_url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"

    def get_tile(self, lat: float, lon: float, zoom: int) -> Optional[Image.Image]:
        """Get a Google satellite imagery tile."""
        x, y = self.latlon_to_tile(lat, lon, zoom)
        url = self.base_url.format(x=x, y=y, z=zoom)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error fetching Google tile: {e}")
            return None


class ESRIImageryProvider(ImageryProvider):
    """Provider for ESRI World Imagery."""

    def __init__(self):
        """Initialize ESRI imagery provider."""
        self.base_url = (
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        )

    def get_tile(self, lat: float, lon: float, zoom: int) -> Optional[Image.Image]:
        """Get an ESRI World Imagery tile."""
        x, y = self.latlon_to_tile(lat, lon, zoom)
        url = self.base_url.format(x=x, y=y, z=zoom)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error fetching ESRI tile: {e}")
            return None


class BingImageryProvider(ImageryProvider):
    """Provider for Bing satellite imagery."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Bing imagery provider.

        Args:
            api_key: Optional Bing Maps API key
        """
        self.api_key = api_key

    def get_tile(self, lat: float, lon: float, zoom: int) -> Optional[Image.Image]:
        """Get a Bing satellite imagery tile."""
        quadkey = self._tile_to_quadkey(*self.latlon_to_tile(lat, lon, zoom), zoom)
        url = f"https://t.ssl.ak.dynamic.tiles.virtualearth.net/comp/ch/{quadkey}?mkt=en-US&it=A,G,L&shading=hill"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Error fetching Bing tile: {e}")
            return None

    @staticmethod
    def _tile_to_quadkey(x: int, y: int, zoom: int) -> str:
        """Convert tile coordinates to Bing quadkey."""
        quadkey = ""
        for i in range(zoom, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (x & mask) != 0:
                digit += 1
            if (y & mask) != 0:
                digit += 2
            quadkey += str(digit)
        return quadkey

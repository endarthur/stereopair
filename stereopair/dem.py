"""
Digital Elevation Model (DEM) providers and handlers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from pyproj import Transformer
import requests
from io import BytesIO


class DEMProvider(ABC):
    """Abstract base class for DEM providers."""

    @abstractmethod
    def get_elevation(
        self, lat: float, lon: float, radius_meters: float = 1000
    ) -> Optional[np.ndarray]:
        """
        Get elevation data around a point.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            radius_meters: Radius around the point to fetch elevation data

        Returns:
            2D numpy array of elevation values in meters, or None if unavailable
        """
        pass

    @abstractmethod
    def get_elevation_at_point(self, lat: float, lon: float) -> Optional[float]:
        """
        Get elevation at a specific point.

        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees

        Returns:
            Elevation in meters, or None if unavailable
        """
        pass


class CustomDEMProvider(DEMProvider):
    """Provider for custom DEM files (GeoTIFF, etc.)."""

    def __init__(self, dem_path: str):
        """
        Initialize custom DEM provider.

        Args:
            dem_path: Path to DEM file (GeoTIFF or other rasterio-supported format)
        """
        self.dem_path = dem_path
        self.dataset = None
        self._load_dem()

    def _load_dem(self):
        """Load the DEM file."""
        try:
            self.dataset = rasterio.open(self.dem_path)
        except Exception as e:
            raise ValueError(f"Error loading DEM file: {e}")

    def get_elevation_at_point(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation at a specific point from the DEM."""
        if self.dataset is None:
            return None

        try:
            # Transform lat/lon to the DEM's CRS
            transformer = Transformer.from_crs("EPSG:4326", self.dataset.crs, always_xy=True)
            x, y = transformer.transform(lon, lat)

            # Get row, col from coordinates
            row, col = self.dataset.index(x, y)

            # Read the elevation value
            elevation = self.dataset.read(1)[row, col]
            return float(elevation)
        except Exception as e:
            print(f"Error getting elevation at point: {e}")
            return None

    def get_elevation(
        self, lat: float, lon: float, radius_meters: float = 1000
    ) -> Optional[np.ndarray]:
        """Get elevation data in a radius around a point."""
        if self.dataset is None:
            return None

        try:
            # Transform center point to DEM CRS
            transformer = Transformer.from_crs("EPSG:4326", self.dataset.crs, always_xy=True)
            center_x, center_y = transformer.transform(lon, lat)

            # Calculate bounds
            bounds = (
                center_x - radius_meters,
                center_y - radius_meters,
                center_x + radius_meters,
                center_y + radius_meters,
            )

            # Read the window
            window = rasterio.windows.from_bounds(*bounds, transform=self.dataset.transform)
            elevation_data = self.dataset.read(1, window=window)

            return elevation_data
        except Exception as e:
            print(f"Error getting elevation data: {e}")
            return None

    def __del__(self):
        """Close the dataset when the object is destroyed."""
        if self.dataset is not None:
            self.dataset.close()


class OpenTopoDataProvider(DEMProvider):
    """Provider for Open Topo Data API (free, open-source elevation API)."""

    def __init__(self, dataset: str = "srtm30m"):
        """
        Initialize Open Topo Data provider.

        Args:
            dataset: Dataset name (e.g., 'srtm30m', 'aster30m', 'etopo1')
        """
        self.dataset = dataset
        self.base_url = "https://api.opentopodata.org/v1/{dataset}"

    def get_elevation_at_point(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation at a specific point using Open Topo Data API."""
        url = self.base_url.format(dataset=self.dataset)
        params = {"locations": f"{lat},{lon}"}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK" and len(data["results"]) > 0:
                return float(data["results"][0]["elevation"])
            return None
        except Exception as e:
            print(f"Error fetching elevation from Open Topo Data: {e}")
            return None

    def get_elevation(
        self, lat: float, lon: float, radius_meters: float = 1000
    ) -> Optional[np.ndarray]:
        """
        Get elevation data in a grid around a point.

        Note: This creates a grid of points and queries the API.
        For large areas, consider using CustomDEMProvider with downloaded data.
        """
        # Create a grid of points
        # Approximate: 1 degree ≈ 111km at equator
        deg_per_meter = 1.0 / 111000.0
        radius_deg = radius_meters * deg_per_meter

        # Create a 10x10 grid
        grid_size = 10
        lats = np.linspace(lat - radius_deg, lat + radius_deg, grid_size)
        lons = np.linspace(lon - radius_deg, lon + radius_deg, grid_size)

        # Build locations string
        locations = []
        for lat_pt in lats:
            for lon_pt in lons:
                locations.append(f"{lat_pt},{lon_pt}")

        url = self.base_url.format(dataset=self.dataset)
        params = {"locations": "|".join(locations)}

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK":
                elevations = [r["elevation"] for r in data["results"]]
                elevation_grid = np.array(elevations).reshape(grid_size, grid_size)
                return elevation_grid
            return None
        except Exception as e:
            print(f"Error fetching elevation grid from Open Topo Data: {e}")
            return None

"""
Automatic DEM tile downloading and caching.

This module handles downloading global DEM data (SRTM, ASTER) and caching it locally.
"""

import os
import requests
from typing import Optional, Tuple
import numpy as np
import rasterio
from rasterio.merge import merge
from pathlib import Path


class DEMTileCache:
    """
    Manager for downloading and caching DEM tiles.
    
    Supports SRTM 30m and ASTER GDEM data from public sources.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize DEM tile cache.
        
        Args:
            cache_dir: Directory for caching DEM tiles. 
                      If None, uses ~/.stereopair/dem_cache
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.stereopair/dem_cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories for different DEM sources
        self.srtm_dir = self.cache_dir / "srtm"
        self.aster_dir = self.cache_dir / "aster"
        self.srtm_dir.mkdir(exist_ok=True)
        self.aster_dir.mkdir(exist_ok=True)
    
    def get_srtm_tile_name(self, lat: float, lon: float) -> str:
        """
        Get SRTM tile name for a given location.
        
        SRTM tiles are 1°x1° and named like N37W122.hgt
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
        
        Returns:
            Tile name (e.g., "N37W122")
        """
        lat_int = int(np.floor(lat))
        lon_int = int(np.floor(lon))
        
        lat_str = f"{'N' if lat_int >= 0 else 'S'}{abs(lat_int):02d}"
        lon_str = f"{'E' if lon_int >= 0 else 'W'}{abs(lon_int):03d}"
        
        return f"{lat_str}{lon_str}"
    
    def download_srtm_tile(self, tile_name: str, source: str = "opentopography") -> Optional[Path]:
        """
        Download an SRTM tile from a public source.
        
        Args:
            tile_name: Tile name (e.g., "N37W122")
            source: Data source ("opentopography" or "usgs")
        
        Returns:
            Path to downloaded tile, or None if unavailable
        """
        tile_path = self.srtm_dir / f"{tile_name}.hgt"
        
        # Check if already cached
        if tile_path.exists():
            return tile_path
        
        print(f"Downloading SRTM tile {tile_name}...")
        
        # Try OpenTopography SRTM API (requires API key for bulk downloads)
        # For now, this is a placeholder - in production, you'd need:
        # 1. OpenTopography API key
        # 2. Or use USGS EarthExplorer API
        # 3. Or use AWS Public Datasets
        
        # AWS Public Dataset URL for SRTM
        # https://registry.opendata.aws/terrain-tiles/
        # https://elevation-tiles-prod.s3.amazonaws.com/skadi/{tile_name}.hgt.gz
        
        if source == "aws":
            url = f"https://elevation-tiles-prod.s3.amazonaws.com/skadi/{tile_name}/{tile_name}.hgt.gz"
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Decompress and save
                import gzip
                decompressed = gzip.decompress(response.content)
                tile_path.write_bytes(decompressed)
                print(f"  Downloaded to {tile_path}")
                return tile_path
                
            except Exception as e:
                print(f"  Failed to download from AWS: {e}")
                return None
        
        print(f"  No download source configured for {tile_name}")
        print(f"  Please manually download SRTM tile and place in {self.srtm_dir}")
        return None
    
    def get_dem_for_bounds(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        source: str = "srtm"
    ) -> Optional[Tuple[np.ndarray, dict]]:
        """
        Get DEM data covering the specified bounds.
        
        Downloads and mosaics tiles as needed.
        
        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude
            max_lon: Maximum longitude
            source: DEM source ("srtm" or "aster")
        
        Returns:
            Tuple of (elevation_array, metadata) or None
            metadata includes transform, crs, etc.
        """
        if source != "srtm":
            print(f"Warning: Only SRTM is currently supported, got {source}")
            return None
        
        # Determine required tiles
        lat_range = range(int(np.floor(min_lat)), int(np.ceil(max_lat)) + 1)
        lon_range = range(int(np.floor(min_lon)), int(np.ceil(max_lon)) + 1)
        
        tile_paths = []
        for lat in lat_range:
            for lon in lon_range:
                tile_name = self.get_srtm_tile_name(lat, lon)
                tile_path = self.download_srtm_tile(tile_name, source="aws")
                if tile_path and tile_path.exists():
                    tile_paths.append(tile_path)
        
        if not tile_paths:
            print("No DEM tiles available for the specified bounds")
            return None
        
        # Load and mosaic tiles
        try:
            # Open all tiles
            src_files = [rasterio.open(str(p)) for p in tile_paths]
            
            # Mosaic them
            mosaic, transform = merge(src_files)
            
            # Close files
            for src in src_files:
                src.close()
            
            # Get metadata from first tile
            with rasterio.open(str(tile_paths[0])) as src:
                crs = src.crs
            
            metadata = {
                'transform': transform,
                'crs': crs,
                'bounds': (min_lon, min_lat, max_lon, max_lat),
            }
            
            # Extract just the elevation band
            elevation = mosaic[0]
            
            return elevation, metadata
            
        except Exception as e:
            print(f"Error mosaicing DEM tiles: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached DEM tiles."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True)
            self.srtm_dir.mkdir(exist_ok=True)
            self.aster_dir.mkdir(exist_ok=True)
            print(f"Cleared DEM cache at {self.cache_dir}")


class CachedDEMProvider:
    """
    DEM provider that automatically downloads and caches global DEM data.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, source: str = "srtm"):
        """
        Initialize cached DEM provider.
        
        Args:
            cache_dir: Directory for caching tiles
            source: DEM source ("srtm" or "aster")
        """
        self.cache = DEMTileCache(cache_dir)
        self.source = source
        self._current_dem = None
        self._current_bounds = None
    
    def get_elevation_at_point(self, lat: float, lon: float) -> Optional[float]:
        """
        Get elevation at a specific point.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
        
        Returns:
            Elevation in meters, or None if unavailable
        """
        # Check if we need to load new DEM
        if (self._current_dem is None or 
            self._current_bounds is None or
            not self._point_in_bounds(lat, lon, self._current_bounds)):
            
            # Load DEM covering this point (with small buffer)
            buffer = 0.1  # degrees
            result = self.cache.get_dem_for_bounds(
                lat - buffer, lat + buffer,
                lon - buffer, lon + buffer,
                source=self.source
            )
            
            if result is None:
                return None
            
            self._current_dem, metadata = result
            self._current_bounds = metadata['bounds']
            self._current_transform = metadata['transform']
        
        # Sample elevation at point
        try:
            from rasterio.transform import rowcol
            row, col = rowcol(self._current_transform, lon, lat)
            
            if (0 <= row < self._current_dem.shape[0] and 
                0 <= col < self._current_dem.shape[1]):
                elevation = self._current_dem[row, col]
                # Filter out no-data values (SRTM uses -32768)
                if elevation > -32000:
                    return float(elevation)
        except Exception as e:
            print(f"Error sampling DEM: {e}")
        
        return None
    
    def get_elevation(
        self, lat: float, lon: float, radius_meters: float = 1000
    ) -> Optional[np.ndarray]:
        """
        Get elevation data in a radius around a point.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            radius_meters: Radius in meters
        
        Returns:
            2D array of elevations, or None
        """
        # Convert radius to degrees (approximate)
        radius_deg = radius_meters / 111000
        
        result = self.cache.get_dem_for_bounds(
            lat - radius_deg, lat + radius_deg,
            lon - radius_deg, lon + radius_deg,
            source=self.source
        )
        
        if result is None:
            return None
        
        elevation, metadata = result
        return elevation
    
    def _point_in_bounds(self, lat: float, lon: float, bounds: tuple) -> bool:
        """Check if point is within bounds."""
        min_lon, min_lat, max_lon, max_lat = bounds
        return (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon)

"""
Stereopair: A Python library for generating stereo pairs from satellite imagery and DEMs.

This library allows users to generate stereo image pairs for photogrammetry and 3D
reconstruction from various satellite imagery sources (Google, Esri, Bing) combined
with Digital Elevation Models (DEMs).
"""

__version__ = "0.1.0"
__author__ = "Arthur Endlein"

from .generator import StereoGenerator
from .imagery import ImageryProvider, GoogleImageryProvider, ESRIImageryProvider, BingImageryProvider
from .dem import DEMProvider, CustomDEMProvider

__all__ = [
    "StereoGenerator",
    "ImageryProvider",
    "GoogleImageryProvider",
    "ESRIImageryProvider",
    "BingImageryProvider",
    "DEMProvider",
    "CustomDEMProvider",
]

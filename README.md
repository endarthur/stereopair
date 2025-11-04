# Stereopair

A Python library to generate stereo image pairs from satellite imagery and Digital Elevation Models (DEMs).

## ⚠️ Current Status

**Perspective Transformation Not Yet Implemented**: This library currently provides the infrastructure for generating stereo pairs from satellite imagery, but the DEM-based perspective transformation is **not yet implemented**. 

Currently, the library:
- ✅ Downloads and caches satellite imagery from Google/ESRI/Bing
- ✅ Calculates stereo camera geometry (baseline, convergence, positions)
- ✅ Downloads and caches SRTM DEM tiles automatically
- ✅ Supports scale-based interface (e.g., `scale="1:5000"`)
- ✅ Generates aerial survey flight lines with multiple positions
- ❌ **Does NOT apply perspective transformation** - orthorectified imagery is returned as-is

**What's Missing**: The transformation from orthorectified satellite imagery to perspective views (as seen from an aerial camera) using DEM elevation data. This requires implementing photogrammetric collinearity equations and ray tracing from camera positions through the DEM surface.

The infrastructure is in place in `perspective.py` for future development.

## Overview

Stereopair allows you to create stereo image pairs for photogrammetric analysis and 3D reconstruction by combining satellite imagery from multiple sources (Google, ESRI, Bing) with elevation data. The library generates left and right stereo images that can be used for depth perception, 3D visualization, and terrain analysis.

## Features

### Implemented
- **Multiple Imagery Providers**: Support for Google Satellite, ESRI World Imagery, and Bing satellite imagery
- **Scale-Based Interface**: Specify scale as `scale=5000` or `scale="1:5000"` instead of zoom levels
- **Standard Photo Sizes**: Predefined ground coverage sizes (small=500m, medium=1km, large=2km, etc.)
- **Automatic DEM Caching**: Downloads and caches SRTM tiles from AWS S3 public dataset
- **Custom DEM Support**: Use your own Digital Elevation Models (GeoTIFF format)
- **Aerial Survey Mode**: Generate series of stereo pairs simulating an aerial photogrammetric survey
- **Flexible Parameters**: Control stereo geometry with configurable base-height ratio and convergence angle
- **Anaglyph Generation**: Automatically create red-cyan 3D anaglyph images
- **Metadata Export**: Save camera parameters and stereo geometry information
- **Simple API**: Easy-to-use Python interface

### Not Yet Implemented
- **DEM-Based Perspective Transformation**: Currently returns orthorectified imagery without applying perspective correction based on terrain elevation. See "Current Status" above.

## Installation

```bash
# Clone the repository
git clone https://github.com/endarthur/stereopair.git
cd stereopair

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

```python
from stereopair import StereoGenerator, GoogleImageryProvider

# Initialize imagery provider
imagery_provider = GoogleImageryProvider()

# Create stereo generator
generator = StereoGenerator(imagery_provider=imagery_provider)

# Generate stereo pair for a location (example: Grand Canyon)
left_image, right_image, metadata = generator.generate_stereo_pair(
    center_lat=36.1069,
    center_lon=-112.1129,
    zoom=17,
    base_height_ratio=0.6,
    convergence_angle=10.0,
    image_size=(800, 800)
)

# Export the images
generator.export_stereo_pair(
    left_image=left_image,
    right_image=right_image,
    output_prefix="my_stereo_pair",
    metadata=metadata,
    export_anaglyph=True
)
```

## Usage Examples

### Using Different Imagery Providers

```python
from stereopair import StereoGenerator, ESRIImageryProvider, BingImageryProvider

# Use ESRI World Imagery
esri_provider = ESRIImageryProvider()
generator = StereoGenerator(imagery_provider=esri_provider)

# Use Bing Satellite Imagery
bing_provider = BingImageryProvider()
generator = StereoGenerator(imagery_provider=bing_provider)
```

### Using Custom DEM

```python
from stereopair import StereoGenerator, GoogleImageryProvider, CustomDEMProvider

# Load your custom DEM (GeoTIFF format)
imagery_provider = GoogleImageryProvider()
dem_provider = CustomDEMProvider(dem_path="path/to/your/dem.tif")

# Create stereo generator with terrain correction
generator = StereoGenerator(
    imagery_provider=imagery_provider,
    dem_provider=dem_provider
)

# Generate stereo pair with terrain correction
left_image, right_image, metadata = generator.generate_stereo_pair(
    center_lat=40.7589,
    center_lon=-73.9851,
    zoom=17
)
```

### Adjusting Stereo Parameters

```python
# More pronounced 3D effect
left_image, right_image, metadata = generator.generate_stereo_pair(
    center_lat=27.9881,
    center_lon=86.9250,
    zoom=16,
    base_height_ratio=0.8,  # Higher ratio = stronger 3D effect
    convergence_angle=15.0,  # Higher angle = more convergence
    image_size=(1024, 1024)
)
```

### Generating Aerial Surveys

Generate a series of stereo pairs along a flight line, simulating an aerial photogrammetric survey:

```python
from stereopair import StereoGenerator, ESRIImageryProvider

# Create generator
imagery_provider = ESRIImageryProvider()
generator = StereoGenerator(imagery_provider=imagery_provider)

# Generate aerial survey along a flight line
survey_results = generator.generate_aerial_survey(
    start_lat=-6.390,
    start_lon=-50.385,
    end_lat=-6.425,
    end_lon=-50.387,
    num_positions=5,        # Number of stereo pairs
    zoom=17,
    overlap_percent=60.0,   # Standard photogrammetric overlap
)

# Export all stereo pairs
generator.export_aerial_survey(
    survey_results=survey_results,
    output_dir="survey_output",
    base_name="my_survey",
    export_anaglyph=True
)
```

This creates multiple stereo pairs with proper overlap for photogrammetric processing.

## API Reference

### StereoGenerator

Main class for generating stereo pairs.

**Methods:**

- `generate_stereo_pair(center_lat, center_lon, zoom, base_height_ratio, convergence_angle, image_size)`: Generate a stereo pair
  - `center_lat` (float): Center latitude in decimal degrees
  - `center_lon` (float): Center longitude in decimal degrees
  - `zoom` (int): Zoom level (15-19 typical for detailed imagery)
  - `base_height_ratio` (float): Ratio of baseline to flying height (0.5-0.8 typical)
  - `convergence_angle` (float): Convergence angle in degrees (5-15 typical)
  - `image_size` (tuple): Output image size in pixels (width, height)

- `generate_aerial_survey(start_lat, start_lon, end_lat, end_lon, num_positions, zoom, base_height_ratio, convergence_angle, image_size, overlap_percent)`: Generate aerial survey
  - `start_lat`, `start_lon` (float): Starting position of flight line
  - `end_lat`, `end_lon` (float): Ending position of flight line
  - `num_positions` (int): Number of stereo pairs along the flight line
  - `overlap_percent` (float): Percentage overlap between consecutive positions (typical 60-80%)

- `export_stereo_pair(left_image, right_image, output_prefix, metadata, export_anaglyph)`: Export stereo pair to files
  - `left_image`: Left stereo image
  - `right_image`: Right stereo image
  - `output_prefix`: Prefix for output filenames
  - `metadata`: Optional metadata dictionary
  - `export_anaglyph`: Whether to export anaglyph image (default: True)

- `export_aerial_survey(survey_results, output_dir, base_name, export_anaglyph)`: Export aerial survey results
  - `survey_results`: List of survey results from generate_aerial_survey()
  - `output_dir`: Directory to save output files
  - `base_name`: Base name for output files

- `create_anaglyph(left_image, right_image, method)`: Create anaglyph 3D image
  - `method`: Anaglyph method ('red-cyan', 'red-green', 'red-blue')

### Imagery Providers

**GoogleImageryProvider**: Google Satellite imagery
**ESRIImageryProvider**: ESRI World Imagery
**BingImageryProvider**: Bing satellite imagery

### DEM Providers

**CustomDEMProvider**: Use custom DEM files (GeoTIFF format)
**OpenTopoDataProvider**: Use OpenTopoData API for elevation data (online)

## Parameters Guide

### Zoom Level
- **15-16**: Regional scale (good for large areas)
- **17-18**: Local scale (good for cities, landmarks)
- **19-20**: Detailed scale (maximum detail, may have limited coverage)

### Base-Height Ratio
- **0.5**: Subtle 3D effect
- **0.6**: Standard stereo (recommended)
- **0.8**: Strong 3D effect (may cause distortion)

### Convergence Angle
- **5-8°**: Gentle convergence
- **10-12°**: Standard convergence (recommended)
- **15-20°**: Strong convergence (may strain viewing)

## Running Examples

The `examples/` directory contains several demonstration scripts:

### Basic Examples
```bash
cd examples
python example_usage.py
```

This will generate several stereo pairs demonstrating different features:
- Basic stereo pair with Google imagery
- Stereo pair with ESRI imagery
- Terrain-corrected stereo pair with custom DEM (if available)

### S11D Mine Example
```bash
cd examples
python s11d_mine_example.py
```

This example demonstrates:
- Single stereo pair over Vale's S11D iron ore mine in Brazil
- Aerial survey generation along a flight line over the mine
- Custom survey with detailed parameters

The S11D mine example showcases the aerial survey feature, generating multiple stereo pairs along defined flight paths over one of the world's largest iron ore mining operations.

### Offline Demo
```bash
cd examples
python demo_offline.py
```

This demo uses synthetic imagery to demonstrate all features without requiring network access.

## Output Files

The library generates:
- `*_left.png`: Left stereo image
- `*_right.png`: Right stereo image
- `*_anaglyph.png`: Red-cyan anaglyph for 3D viewing (use red-cyan 3D glasses)
- `*_metadata.json`: Camera parameters and stereo geometry

## Requirements

- Python 3.8+
- numpy
- pillow
- requests
- rasterio (for DEM support)
- pyproj (for coordinate transformations)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This library uses publicly available satellite imagery from:
- Google Maps
- ESRI World Imagery
- Bing Maps

Please respect the terms of service of these providers when using the library.

## Citation

If you use this library in your research, please cite:

```
@software{stereopair,
  author = {Endlein, Arthur},
  title = {Stereopair: A Python library for generating stereo pairs from satellite imagery},
  year = {2025},
  url = {https://github.com/endarthur/stereopair}
}
```
# API Documentation

## Overview

The Stereopair library provides a Python API for generating stereo image pairs from satellite imagery and Digital Elevation Models (DEMs). This document describes the main classes and methods available in the library.

## Core Classes

### StereoGenerator

Main class for generating stereo image pairs.

```python
from stereopair import StereoGenerator, GoogleImageryProvider

generator = StereoGenerator(
    imagery_provider=GoogleImageryProvider(),
    dem_provider=None  # Optional
)
```

#### Constructor Parameters

- `imagery_provider` (ImageryProvider): Provider for satellite imagery (required)
- `dem_provider` (DEMProvider, optional): Provider for DEM data for terrain correction

#### Methods

##### `generate_stereo_pair()`

Generate a stereo pair of images centered at a given location.

```python
left_image, right_image, metadata = generator.generate_stereo_pair(
    center_lat=36.1069,
    center_lon=-112.1129,
    zoom=17,
    base_height_ratio=0.6,
    convergence_angle=10.0,
    image_size=(512, 512)
)
```

**Parameters:**

- `center_lat` (float): Center latitude in decimal degrees
- `center_lon` (float): Center longitude in decimal degrees
- `zoom` (int): Zoom level (15-19 typical, higher = more detail)
- `base_height_ratio` (float): Ratio of baseline to flying height (0.5-0.8)
  - 0.5: Subtle 3D effect
  - 0.6: Standard (recommended)
  - 0.8: Strong 3D effect
- `convergence_angle` (float): Convergence angle in degrees (5-15 typical)
  - 5-8°: Gentle convergence
  - 10-12°: Standard (recommended)
  - 15-20°: Strong convergence
- `image_size` (tuple): Output image size in pixels (width, height)

**Returns:**

Tuple of (left_image, right_image, metadata):
- `left_image` (PIL.Image): Left stereo image
- `right_image` (PIL.Image): Right stereo image
- `metadata` (dict): Camera parameters and stereo geometry

##### `create_anaglyph()`

Create an anaglyph 3D image from a stereo pair.

```python
anaglyph = generator.create_anaglyph(
    left_image=left_image,
    right_image=right_image,
    method="red-cyan"
)
```

**Parameters:**

- `left_image` (PIL.Image): Left stereo image
- `right_image` (PIL.Image): Right stereo image
- `method` (str): Anaglyph method
  - `"red-cyan"`: Red-cyan anaglyph (default, most common)
  - `"red-green"`: Red-green anaglyph
  - `"red-blue"`: Red-blue anaglyph

**Returns:**

- `anaglyph` (PIL.Image): Anaglyph image for 3D viewing with colored glasses

##### `export_stereo_pair()`

Export stereo pair images to files.

```python
generator.export_stereo_pair(
    left_image=left_image,
    right_image=right_image,
    output_prefix="my_stereo",
    metadata=metadata,
    export_anaglyph=True
)
```

**Parameters:**

- `left_image` (PIL.Image): Left stereo image
- `right_image` (PIL.Image): Right stereo image
- `output_prefix` (str): Prefix for output filenames
- `metadata` (dict, optional): Metadata to save as JSON
- `export_anaglyph` (bool): Whether to export anaglyph image (default: True)

**Output Files:**

- `{prefix}_left.png`: Left stereo image
- `{prefix}_right.png`: Right stereo image
- `{prefix}_anaglyph.png`: Red-cyan anaglyph (if export_anaglyph=True)
- `{prefix}_metadata.json`: Camera parameters and geometry (if metadata provided)

---

## Imagery Providers

### ImageryProvider (Abstract Base Class)

Base class for all imagery providers.

#### Methods

##### `get_tile(lat, lon, zoom)`

Get a satellite imagery tile at the specified location.

**Parameters:**
- `lat` (float): Latitude in decimal degrees
- `lon` (float): Longitude in decimal degrees
- `zoom` (int): Zoom level (0-20)

**Returns:**
- PIL.Image or None

##### Static Methods

`latlon_to_tile(lat, lon, zoom)`: Convert lat/lon to tile coordinates
`tile_to_latlon(x, y, zoom)`: Convert tile coordinates to lat/lon

---

### GoogleImageryProvider

Provider for Google Satellite imagery.

```python
from stereopair import GoogleImageryProvider

provider = GoogleImageryProvider(api_key=None)
```

**Parameters:**
- `api_key` (str, optional): Google Maps API key

**Note:** The free tile server is used by default. For production use, you should use a valid API key.

---

### ESRIImageryProvider

Provider for ESRI World Imagery.

```python
from stereopair import ESRIImageryProvider

provider = ESRIImageryProvider()
```

**Note:** Uses the public ESRI World Imagery service.

---

### BingImageryProvider

Provider for Bing satellite imagery.

```python
from stereopair import BingImageryProvider

provider = BingImageryProvider(api_key=None)
```

**Parameters:**
- `api_key` (str, optional): Bing Maps API key

---

## DEM Providers

### DEMProvider (Abstract Base Class)

Base class for all DEM providers.

#### Methods

##### `get_elevation(lat, lon, radius_meters=1000)`

Get elevation data around a point.

**Parameters:**
- `lat` (float): Latitude in decimal degrees
- `lon` (float): Longitude in decimal degrees
- `radius_meters` (float): Radius around the point

**Returns:**
- numpy.ndarray: 2D array of elevation values in meters

##### `get_elevation_at_point(lat, lon)`

Get elevation at a specific point.

**Parameters:**
- `lat` (float): Latitude in decimal degrees
- `lon` (float): Longitude in decimal degrees

**Returns:**
- float: Elevation in meters or None

---

### CustomDEMProvider

Provider for custom DEM files (GeoTIFF format).

```python
from stereopair import CustomDEMProvider

dem_provider = CustomDEMProvider(dem_path="/path/to/dem.tif")
```

**Parameters:**
- `dem_path` (str): Path to DEM file (GeoTIFF or rasterio-supported format)

**Supported Formats:**
- GeoTIFF (.tif, .tiff)
- Any format supported by rasterio

---

### OpenTopoDataProvider

Provider for Open Topo Data API (free elevation API).

```python
from stereopair.dem import OpenTopoDataProvider

dem_provider = OpenTopoDataProvider(dataset="srtm30m")
```

**Parameters:**
- `dataset` (str): Dataset name
  - `"srtm30m"`: SRTM 30m resolution (default)
  - `"aster30m"`: ASTER 30m resolution
  - `"etopo1"`: ETOPO1 global relief

**Note:** This provider requires internet access and has rate limits.

---

## Metadata Structure

The metadata dictionary returned by `generate_stereo_pair()` contains:

```python
{
    "center": {
        "lat": 36.1069,
        "lon": -112.1129
    },
    "left_camera": {
        "lat": 36.1069,
        "lon": -112.1296,
        "view_center_lon": -112.1153
    },
    "right_camera": {
        "lat": 36.1069,
        "lon": -112.0962,
        "view_center_lon": -112.1105
    },
    "geometry": {
        "baseline_meters": 3000.0,
        "flying_height_meters": 5000,
        "base_height_ratio": 0.6,
        "convergence_angle_degrees": 10.0,
        "gsd_meters": 0.9649
    },
    "zoom": 17
}
```

**Fields:**
- `center`: Center point coordinates
- `left_camera`: Left camera position and view direction
- `right_camera`: Right camera position and view direction
- `geometry`: Stereo geometry parameters
  - `baseline_meters`: Distance between cameras
  - `flying_height_meters`: Virtual camera height
  - `base_height_ratio`: Baseline to height ratio
  - `convergence_angle_degrees`: Angle between camera axes
  - `gsd_meters`: Ground sampling distance (meters per pixel)
- `zoom`: Zoom level used

---

## Usage Examples

### Basic Stereo Pair

```python
from stereopair import StereoGenerator, GoogleImageryProvider

# Create generator
imagery_provider = GoogleImageryProvider()
generator = StereoGenerator(imagery_provider=imagery_provider)

# Generate stereo pair
left, right, metadata = generator.generate_stereo_pair(
    center_lat=36.1069,
    center_lon=-112.1129,
    zoom=17
)

# Export images
generator.export_stereo_pair(left, right, "output")
```

### With Custom DEM

```python
from stereopair import StereoGenerator, GoogleImageryProvider, CustomDEMProvider

# Create providers
imagery_provider = GoogleImageryProvider()
dem_provider = CustomDEMProvider(dem_path="elevation.tif")

# Create generator with DEM
generator = StereoGenerator(
    imagery_provider=imagery_provider,
    dem_provider=dem_provider
)

# Generate terrain-corrected stereo pair
left, right, metadata = generator.generate_stereo_pair(
    center_lat=40.7589,
    center_lon=-73.9851,
    zoom=17
)
```

### Different Imagery Provider

```python
from stereopair import StereoGenerator, ESRIImageryProvider

# Use ESRI instead of Google
imagery_provider = ESRIImageryProvider()
generator = StereoGenerator(imagery_provider=imagery_provider)

left, right, metadata = generator.generate_stereo_pair(
    center_lat=27.9881,
    center_lon=86.9250,
    zoom=16,
    base_height_ratio=0.7,  # Stronger 3D effect
    convergence_angle=12.0
)
```

### Create Custom Anaglyph

```python
from stereopair import StereoGenerator, GoogleImageryProvider

generator = StereoGenerator(imagery_provider=GoogleImageryProvider())
left, right, _ = generator.generate_stereo_pair(
    center_lat=36.1069,
    center_lon=-112.1129,
    zoom=17
)

# Create different anaglyph types
red_cyan = generator.create_anaglyph(left, right, method="red-cyan")
red_green = generator.create_anaglyph(left, right, method="red-green")
red_blue = generator.create_anaglyph(left, right, method="red-blue")

red_cyan.save("anaglyph_rc.png")
red_green.save("anaglyph_rg.png")
red_blue.save("anaglyph_rb.png")
```

---

## Constants

The following constants are defined in `stereopair.generator`:

- `EARTH_CIRCUMFERENCE_METERS = 40075017`: Earth's equatorial circumference
- `METERS_PER_DEGREE_EQUATOR = 111000`: Approximate meters per degree at equator
- `DEFAULT_FLYING_HEIGHT_METERS = 5000`: Default virtual camera height

These can be imported if needed:

```python
from stereopair.generator import EARTH_CIRCUMFERENCE_METERS, DEFAULT_FLYING_HEIGHT_METERS
```

---

## Error Handling

All methods gracefully handle errors and will:
- Return `None` for images if fetching fails
- Print error messages to console
- Continue execution when possible

Example:

```python
left, right, metadata = generator.generate_stereo_pair(...)

if left is None or right is None:
    print("Failed to generate stereo pair")
else:
    # Process images
    generator.export_stereo_pair(left, right, "output")
```

---

## Best Practices

1. **Choose appropriate zoom levels:**
   - Zoom 15-16: Regional features
   - Zoom 17-18: Local features (recommended)
   - Zoom 19-20: High detail (limited availability)

2. **Balance stereo parameters:**
   - Higher base/height ratio = stronger 3D but more distortion
   - Higher convergence angle = more overlap but viewing strain

3. **Use DEM for terrain:**
   - Provides more accurate stereo pairs for mountainous areas
   - CustomDEMProvider is faster than API-based providers

4. **Check imagery availability:**
   - Not all locations have high-resolution imagery
   - Different providers may have different coverage

5. **Respect API terms:**
   - Use API keys for production applications
   - Be aware of rate limits for online services
   - Cache results when possible

---

## License

MIT License - See LICENSE file for details.

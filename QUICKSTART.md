# Stereopair Quick Start Guide

Get started with the Stereopair library in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/endarthur/stereopair.git
cd stereopair

# Install the package
pip install -e .
```

## Basic Usage

### 1. Generate Your First Stereo Pair

```python
from stereopair import StereoGenerator, GoogleImageryProvider

# Create a stereo generator
imagery_provider = GoogleImageryProvider()
generator = StereoGenerator(imagery_provider=imagery_provider)

# Generate stereo pair (example: Grand Canyon)
left, right, metadata = generator.generate_stereo_pair(
    center_lat=36.1069,
    center_lon=-112.1129,
    zoom=17,
    base_height_ratio=0.6,
    convergence_angle=10.0,
    image_size=(800, 800)
)

# Export the results
generator.export_stereo_pair(
    left_image=left,
    right_image=right,
    output_prefix="grand_canyon",
    metadata=metadata,
    export_anaglyph=True
)
```

This will create:
- `grand_canyon_left.png` - Left stereo image
- `grand_canyon_right.png` - Right stereo image
- `grand_canyon_anaglyph.png` - 3D anaglyph (view with red-cyan glasses!)
- `grand_canyon_metadata.json` - Camera parameters

### 2. Try the Offline Demo

No internet? No problem! Run the offline demo:

```bash
python examples/demo_offline.py
```

This uses synthetic imagery to demonstrate all features without requiring network access.

### 3. Explore Different Imagery Sources

```python
from stereopair import StereoGenerator, ESRIImageryProvider

# Use ESRI World Imagery instead
imagery_provider = ESRIImageryProvider()
generator = StereoGenerator(imagery_provider=imagery_provider)

# Generate stereo pair (example: Mount Everest)
left, right, metadata = generator.generate_stereo_pair(
    center_lat=27.9881,
    center_lon=86.9250,
    zoom=16
)
```

### 4. Add Terrain Data (Optional)

```python
from stereopair import StereoGenerator, GoogleImageryProvider, CustomDEMProvider

# Load your DEM file
imagery_provider = GoogleImageryProvider()
dem_provider = CustomDEMProvider(dem_path="your_dem.tif")

# Create generator with terrain correction
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

## Parameter Guide

### Zoom Level
- **15-16**: Regional scale (large areas)
- **17-18**: Local scale (cities, landmarks) ⭐ **Recommended**
- **19-20**: Detailed scale (maximum detail)

### Base-Height Ratio
- **0.5**: Subtle 3D effect
- **0.6**: Standard stereo ⭐ **Recommended**
- **0.8**: Strong 3D effect

### Convergence Angle
- **5-8°**: Gentle convergence
- **10-12°**: Standard convergence ⭐ **Recommended**
- **15-20°**: Strong convergence

## Viewing Your Results

### Anaglyph Images
Use red-cyan 3D glasses to view the `*_anaglyph.png` files for a 3D effect!

### Stereo Pairs
View left and right images side-by-side:
- Cross-eye viewing: Left image on right, right image on left
- Parallel viewing: Left image on left, right image on right
- Use a stereoscope for best results

## Example Locations to Try

```python
# Grand Canyon, USA
center_lat, center_lon = 36.1069, -112.1129

# Mount Everest, Nepal
center_lat, center_lon = 27.9881, 86.9250

# Uluru, Australia  
center_lat, center_lon = -25.3444, 131.0369

# Christ the Redeemer, Brazil
center_lat, center_lon = -22.9519, -43.2105

# Machu Picchu, Peru
center_lat, center_lon = -13.1631, -72.5450
```

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Check the [API.md](API.md) for complete API documentation
- Explore [examples/example_usage.py](examples/example_usage.py) for more examples
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute to the project

## Troubleshooting

### Issue: No imagery downloaded
- Check your internet connection
- Some locations may not have high-resolution imagery
- Try a different imagery provider (ESRI, Bing)
- Try a lower zoom level (16 instead of 18)

### Issue: DEM file not loading
- Ensure the file is in GeoTIFF format
- Check the file path is correct
- Verify the DEM covers your area of interest

### Issue: Import errors
- Make sure you installed the package: `pip install -e .`
- Check all dependencies are installed: `pip install -r requirements.txt`

## Need Help?

- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation in [API.md](API.md)

Happy stereo pair generation! 🌍✨

"""
Example: Vale's S11D Mine Aerial Survey

This example demonstrates generating an aerial survey over Vale's S11D iron ore mine
in Carajás, Pará, Brazil - one of the world's largest iron ore mining operations.

The S11D mine is located in the Serra Sul region and represents a major mining
development with distinctive open-pit features visible from satellite imagery.
"""

from stereopair import StereoGenerator, GoogleImageryProvider, ESRIImageryProvider
import sys
import os


def example_s11d_single_stereo_pair():
    """Generate a single stereo pair over the S11D mine."""
    print("=" * 70)
    print("Example 1: Single Stereo Pair - Vale S11D Mine")
    print("=" * 70)

    # Vale S11D Mine coordinates (approximate center)
    # Location: Carajás, Pará, Brazil
    center_lat = -6.4067
    center_lon = -50.3858

    print(f"\nTarget: Vale S11D Iron Ore Mine")
    print(f"Location: Carajás, Pará, Brazil")
    print(f"Coordinates: {center_lat}°S, {abs(center_lon)}°W")

    # Create stereo generator with ESRI imagery (often has good coverage of remote areas)
    print("\nInitializing imagery provider...")
    imagery_provider = ESRIImageryProvider()
    generator = StereoGenerator(imagery_provider=imagery_provider)

    # Generate stereo pair
    print("\nGenerating stereo pair...")
    left, right, metadata = generator.generate_stereo_pair(
        center_lat=center_lat,
        center_lon=center_lon,
        zoom=17,  # High detail to see mine features
        base_height_ratio=0.65,  # Slightly higher for better 3D effect on terrain
        convergence_angle=11.0,
        image_size=(1024, 1024),
    )

    if left and right:
        # Export the stereo pair
        output_dir = "s11d_mine_output"
        os.makedirs(output_dir, exist_ok=True)
        output_prefix = os.path.join(output_dir, "s11d_mine")

        generator.export_stereo_pair(
            left_image=left,
            right_image=right,
            output_prefix=output_prefix,
            metadata=metadata,
            export_anaglyph=True,
        )

        print("\n✓ Stereo pair generated successfully!")
        print(f"\nOutput files saved to: {output_dir}/")
        print(f"  - s11d_mine_left.png")
        print(f"  - s11d_mine_right.png")
        print(f"  - s11d_mine_anaglyph.png (view with red-cyan 3D glasses)")
        print(f"  - s11d_mine_metadata.json")

        print(f"\nStereo Geometry:")
        print(f"  Baseline: {metadata['geometry']['baseline_meters']:.2f} meters")
        print(f"  Flying Height: {metadata['geometry']['flying_height_meters']:.2f} meters")
        print(f"  GSD: {metadata['geometry']['gsd_meters']:.4f} meters/pixel")
    else:
        print("\n✗ Failed to generate stereo pair")
        print("Note: This may be due to network connectivity or imagery availability")


def example_s11d_aerial_survey():
    """Generate an aerial survey over the S11D mine area."""
    print("\n" + "=" * 70)
    print("Example 2: Aerial Survey - Vale S11D Mine")
    print("=" * 70)

    # Define flight line over the mine
    # This covers the main pit area from north to south
    start_lat = -6.390  # Northern end
    start_lon = -50.385
    end_lat = -6.425    # Southern end
    end_lon = -50.387

    print(f"\nTarget: Vale S11D Iron Ore Mine - Aerial Survey")
    print(f"Flight line: North to South over main pit")
    print(f"Start: {start_lat}°S, {abs(start_lon)}°W")
    print(f"End: {end_lat}°S, {abs(end_lon)}°W")

    # Create stereo generator
    print("\nInitializing imagery provider...")
    imagery_provider = ESRIImageryProvider()
    generator = StereoGenerator(imagery_provider=imagery_provider)

    # Generate aerial survey
    print("\nGenerating aerial survey...")
    survey_results = generator.generate_aerial_survey(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
        num_positions=5,  # 5 stereo pairs along the flight line
        zoom=17,
        base_height_ratio=0.65,
        convergence_angle=11.0,
        image_size=(800, 800),
        overlap_percent=60.0,  # Standard 60% overlap
    )

    if survey_results:
        # Export the survey
        output_dir = "s11d_mine_survey"
        generator.export_aerial_survey(
            survey_results=survey_results,
            output_dir=output_dir,
            base_name="s11d_survey",
            export_anaglyph=True,
        )

        print("\n✓ Aerial survey completed successfully!")
        print(f"\nGenerated {len(survey_results)} stereo pairs")
        print(f"Output directory: {output_dir}/")
        print(f"\nFiles created:")
        print(f"  - s11d_survey_pos000_left.png, *_right.png, *_anaglyph.png")
        print(f"  - s11d_survey_pos001_left.png, *_right.png, *_anaglyph.png")
        print(f"  - ... (one set per position)")
        print(f"  - s11d_survey_survey_overview.json (survey metadata)")
        print(f"\nView anaglyph images with red-cyan 3D glasses for 3D effect!")
    else:
        print("\n✗ Failed to generate aerial survey")
        print("Note: This may be due to network connectivity or imagery availability")


def example_s11d_custom_survey():
    """Generate a custom aerial survey with specific parameters."""
    print("\n" + "=" * 70)
    print("Example 3: Custom Aerial Survey - S11D Mine Detailed")
    print("=" * 70)

    # Define a cross-pattern survey (east-west line)
    start_lat = -6.4067
    start_lon = -50.400  # Western end
    end_lat = -6.4067
    end_lon = -50.370    # Eastern end

    print(f"\nTarget: Vale S11D Iron Ore Mine - East-West Survey")
    print(f"Flight line: East-West across mine facilities")

    # Create stereo generator with Google imagery as alternative
    print("\nInitializing imagery provider...")
    imagery_provider = GoogleImageryProvider()
    generator = StereoGenerator(imagery_provider=imagery_provider)

    # Generate detailed survey with more positions
    print("\nGenerating detailed aerial survey...")
    survey_results = generator.generate_aerial_survey(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
        num_positions=7,  # More positions for detailed coverage
        zoom=18,  # Higher zoom for more detail
        base_height_ratio=0.6,
        convergence_angle=10.0,
        image_size=(1024, 1024),
        overlap_percent=70.0,  # Higher overlap for better tie points
    )

    if survey_results:
        # Export the survey
        output_dir = "s11d_mine_detailed_survey"
        generator.export_aerial_survey(
            survey_results=survey_results,
            output_dir=output_dir,
            base_name="s11d_detailed",
            export_anaglyph=True,
        )

        print("\n✓ Detailed aerial survey completed!")
        print(f"\nGenerated {len(survey_results)} high-resolution stereo pairs")
        print(f"Output directory: {output_dir}/")
    else:
        print("\n✗ Failed to generate aerial survey")


def main():
    """Run all S11D mine examples."""
    print("\n" + "=" * 70)
    print("VALE S11D MINE - STEREO PAIR GENERATION EXAMPLES")
    print("=" * 70)
    print("\nThis example demonstrates stereo pair generation over Vale's S11D")
    print("iron ore mine in Carajás, Brazil - one of the world's largest and")
    print("most modern mining operations.")
    print("\nNote: Requires internet connection to fetch satellite imagery.")

    try:
        # Run examples
        example_s11d_single_stereo_pair()
        example_s11d_aerial_survey()
        example_s11d_custom_survey()

        print("\n" + "=" * 70)
        print("All examples completed!")
        print("=" * 70)
        print("\nYou can view the generated stereo pairs in the output directories:")
        print("  - s11d_mine_output/")
        print("  - s11d_mine_survey/")
        print("  - s11d_mine_detailed_survey/")
        print("\nUse red-cyan 3D glasses to view the anaglyph images!")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

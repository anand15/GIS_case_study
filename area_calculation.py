import rasterio
import numpy as np
import pandas as pd

def calculate_land_use_area(raster_path):
    """
    Calculates the area of different land use classes in a classified raster by inferring pixel size.

    Args:
        raster_path (str): Path to the classified raster file.

    Returns:
        DataFrame: A summary table with land use classes and their respective areas.
    """

    with rasterio.open(raster_path) as src:
        land_use_array = src.read(1)  # Read the first band
        nodata_value = src.nodata  # Get the NoData value

        # Infer pixel size from raster transform
        pixel_size_x, pixel_size_y = abs(src.transform.a), abs(src.transform.e)
        pixel_area = pixel_size_x * pixel_size_y  # Compute pixel area

    # Mask out NoData values
    if nodata_value is not None:
        land_use_array = np.where(land_use_array == nodata_value, np.nan, land_use_array)

    # Get unique land use classes and their counts
    unique_classes, counts = np.unique(land_use_array[~np.isnan(land_use_array)], return_counts=True)

    # Compute area for each land use class
    areas = counts * pixel_area

    # Create a DataFrame to store results
    land_use_summary = pd.DataFrame({
        "Land Use Class": unique_classes.astype(int),  # Ensure integer representation
        "Pixel Count": counts,
        "Area (sq meters)": areas
    })

    return land_use_summary

# List of raster files
raster_paths = [
    "file1.tif",
    "file2.tif",
    "file3.tif",
    "file4",
    "file5.tif",
    "file6.tif"
]

# Process each raster and store results
all_summaries = []
for raster in raster_paths:
    summary = calculate_land_use_area(raster)
    summary["Raster Name"] = raster  # Add raster name for identification
    all_summaries.append(summary)

# Combine all summaries into one DataFrame
final_summary = pd.concat(all_summaries, ignore_index=True)

# Save results to CSV
final_summary.to_csv("land_use_area_summary.csv", index=False)


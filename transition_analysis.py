import rasterio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def generate_transition_raster_and_table(raster1_path, raster2_path, output_raster, output_csv):
    """
    Generates a transition raster and a CSV table interpreting the values.

    Args:
        raster1_path (str): Path to the first raster layer.
        raster2_path (str): Path to the second raster layer.
        output_raster (str): Path to the output transition raster.
        output_csv (str): Path to the output CSV file.
        output_image (str): Path to the output image visualization.
    """

    with rasterio.open(raster1_path) as src1, rasterio.open(raster2_path) as src2:
        # Read raster data
        array1 = src1.read(1).astype(np.uint16)
        array2 = src2.read(1).astype(np.uint16)

        # Ensure NoData values are properly handled
        nodata_value = src1.nodata if src1.nodata is not None else 65535
        array1[array1 == nodata_value] = 0  # Replace nodata with 0 for processing
        array2[array2 == nodata_value] = 0  

        # Create transition raster
        combined = array1 * 100 + array2

        # Update metadata for output raster
        profile = src1.profile
        profile.update(count=1, dtype=rasterio.uint16, nodata=65535)

        # Save transition raster
        with rasterio.open(output_raster, 'w', **profile) as dst:
            dst.write(combined.astype(rasterio.uint16), 1)

       # Extract unique transition values
        unique_values = np.unique(combined)

        # Create a mapping dictionary for transition values
        transition_dict = {value: f"Class {value // 100} to Class {value % 100}" for value in unique_values}

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(list(transition_dict.items()), columns=['Transition Value', 'Transition'])
        df.to_csv(output_csv, index=False)

# Example usage
raster1_path = "raster1.tif"
raster2_path = "raster2.tif"
output_raster = "outpt_transition_raster.tif"
output_csv = "output_transition_table.csv"

generate_transition_raster_and_table(raster1_path, raster2_path, output_raster, output_csv)

###########
# Transition matrix

def generate_transition_matrix(raster1_path, raster2_path, year1, year2):
    """
    Generates a land use transition matrix based on two raster layers.

    Args:
        raster1_path (str): Path to the first raster layer.
        raster2_path (str): Path to the second raster layer.
        year1 (int): Year of the first raster layer.
        year2 (int): Year of the second raster layer.

    Returns:
        np.ndarray: A transition matrix.
    """

    # Open raster layers
    with rasterio.open(raster1_path) as src1, rasterio.open(raster2_path) as src2:
        # Read raster data
        array1 = src1.read(1)
        array2 = src2.read(1)

        # Get unique land use classes
        classes = np.unique(np.concatenate((array1, array2)))

        # Create an empty transition matrix
        transition_matrix = np.zeros((len(classes), len(classes)), dtype=int)

        # Fill the transition matrix
        for i in range(len(classes)):
            for j in range(len(classes)):
                transition_matrix[i, j] = np.sum((array1 == classes[i]) & (array2 == classes[j]))

    # Create a pandas DataFrame from the transition matrix
    df = pd.DataFrame(transition_matrix, index=classes, columns=classes)

    # Save the DataFrame as a CSV file
    df.to_csv(f"final_transition_matrix_{year1}_{year2}.csv")

    return transition_matrix


# Example usage
raster1_path = "raster1.tif"
raster2_path = "raster2.tif"
year1 = 2014
year2 = 2024
transition_matrix = generate_transition_matrix(raster1_path, raster2_path, year1, year2)

import os
import shutil

# Define the path to the main folder containing all sensor data
main_folder = 'Carla_Data'
# Define the path to the folder where all images will be saved
output_folder = 'Dataset_Images'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize a counter for naming the images
counter = 1

# Walk through the directory structure
for root, dirs, files in os.walk(main_folder):
    for file in files:
        # Check if the file is a PNG image
        if file.endswith('.png'):
            # Extract the full path to the image
            full_image_path = os.path.join(root, file)

            # Extract the folder and camera name from the path
            folder_name = os.path.basename(os.path.dirname(root))
            camera_name = os.path.basename(root).replace('camera_', '')

            # Split the folder name into its components
            folder_parts = folder_name.split('_')

            # Extract town number (e.g., "02" from "town_02")
            town_number = folder_parts[3]

            # Determine part number or default to "00" if not present
            if 'part' in folder_parts:
                part_index = folder_parts.index('part')
                part_number = folder_parts[part_index + 1]
                time_of_day = folder_parts[part_index + 2]
            else:
                part_number = '00'
                time_of_day = folder_parts[6]

            # Create the new filename using the placeholders
            new_filename = f"{counter:04d}_town_{town_number}_part_{part_number}_{time_of_day}_{camera_name}.png"

            # Define the full path for the new image location
            new_image_path = os.path.join(output_folder, new_filename)

            # Copy and rename the image to the output folder
            shutil.copyfile(full_image_path, new_image_path)

            # Increment the counter for the next image
            counter += 1

print(f"Collected images have been saved to the '{output_folder}' directory.")

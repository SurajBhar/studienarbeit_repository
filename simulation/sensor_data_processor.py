import os
import pandas as pd
import logging
import sys
import settings
sys.path.append(settings.CARLA_EGG_PATH)

class SensorDataProcessor:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def save_dataframe_to_disk(self, df, file_path):
        """ Saves the DataFrame to disk at the specified path in CSV format. """
        try:
            df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
            df.drop(df.index, inplace=True)  # Clear the DataFrame after saving
            logging.info(f"Data saved successfully to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save DataFrame to {file_path}: {e}")

    def process_camera_data(self, data, sensor_id, role_name, current_frame):
        """ Processes and stores camera data including all relevant sensor attributes. """
        try:
            # Use role_name to create a meaningful directory
            camera_dir = os.path.join(self.data_dir, f"camera_{role_name}")
            os.makedirs(camera_dir, exist_ok=True)
            image_path = os.path.join(camera_dir, f"{data.frame}.png")
            data.save_to_disk(image_path)
            logging.info(f"Image saved to {image_path}")

            # Extract transform details
            location = data.transform.location
            rotation = data.transform.rotation

            # Create DataFrame for a single data point
            df = pd.DataFrame([{
                'sensor_id': sensor_id,
                'role_name': role_name,
                'captured_frame': current_frame,
                'frame': data.frame,
                'timestamp': data.timestamp,
                'image_path': image_path,
                'width': data.width,
                'height': data.height,
                'fov': data.fov,
                'location_x': location.x,
                'location_y': location.y,
                'location_z': location.z,
                'rotation_pitch': rotation.pitch,
                'rotation_yaw': rotation.yaw,
                'rotation_roll': rotation.roll
            }])

            # Save DataFrame to disk
            self.save_dataframe_to_disk(df, os.path.join(camera_dir, 'camera_data.csv'))

        except Exception as e:
            logging.error(f"Failed to process camera data for sensor {sensor_id} ({role_name}) at frame {current_frame}: {e}")

    def process_radar_data(self, radar_data, sensor_id, role_name, current_frame):
        """ Processes and stores radar data. """
        try:
            radar_dir = os.path.join(self.data_dir, f"radar_{role_name}")
            os.makedirs(radar_dir, exist_ok=True)

            # Create DataFrame for radar data points
            records = [{
                'sensor_id': sensor_id,
                'role_name': role_name,
                'captured_frame': current_frame,
                'velocity': data.velocity,
                'altitude': data.altitude,
                'azimuth': data.azimuth,
                'depth': data.depth
            } for data in radar_data]
            df = pd.DataFrame(records)

            # Save DataFrame to disk
            self.save_dataframe_to_disk(df, os.path.join(radar_dir, 'radar_data.csv'))

        except Exception as e:
            logging.error(f"Failed to process radar data for sensor {sensor_id} ({role_name}) at frame {current_frame}: {e}")

    def process_ultrasonic_data(self, data, sensor_id, role_name, current_frame):
        """ Processes and stores ultrasonic sensor data, which are simulated using RadarMeasurement. """
        try:
            ultrasonic_dir = os.path.join(self.data_dir, f"ultrasonic_{role_name}")
            os.makedirs(ultrasonic_dir, exist_ok=True)

            # Create DataFrame for ultrasonic data points
            records = [{'sensor_id': sensor_id, 'role_name': role_name, 'captured_frame': current_frame, 'depth': data.depth} for data in data]
            df = pd.DataFrame(records)

            # Save DataFrame to disk
            self.save_dataframe_to_disk(df, os.path.join(ultrasonic_dir, f"ultrasonic_data.csv"))

        except Exception as e:
            logging.error(f"Failed to process ultrasonic data for sensor {sensor_id} ({role_name}) at frame {current_frame}: {e}")

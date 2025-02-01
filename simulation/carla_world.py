import glob
import os
import sys
import json
import logging
import random
import numpy as np
import carla
from Sensor_Base import CameraSensor, RadarSensor, UltrasonicSensor
from set_synchronous_mode import CarlaSyncMode
from WeatherSelector import WeatherSelector
from sensor_data_processor import SensorDataProcessor
from spawn_npc import NPCClass

# Setup logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

import settings
sys.path.append(settings.CARLA_EGG_PATH)

SENSOR_CONFIG_PATH = {
    "camera": "configs/camera_config.json",
    "radar": "configs/radar_config.json",
    "ultrasonic": "configs/ultrasonic_config.json"
}

class CarlaWorld:
    def __init__(self, host='localhost', port=2000, autopilot=True, target_speed=80.0):
        """
        Initializes the CARLA client and sets up the simulation environment to always load Town01.

        Args:
            host (str): The IP address of the CARLA server.
            port (int): The port on which the CARLA server is running.
        """
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.set_town('Town06')
        self.data_dir = 'sensor_data_town_01_test'
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_processor = SensorDataProcessor(self.data_dir)
        self.blueprint_library = self.world.get_blueprint_library()
        self.NPC = None
        self.weather_options = WeatherSelector().get_weather_options()
        self.vehicle = None
        self.sensors_list = []
        self.autopilot = autopilot
        self.target_speed = target_speed  # Set the target speed
        self.setup_vehicle()
        self.setup_sensors()

    def set_town(self, town_name):
        """
        Loads the specified CARLA town map.

        Args:
            town_name (str): The name of the town map to load, e.g., 'Town01'.
        """
        self.world = self.client.load_world(town_name)
        logging.info(f'{town_name} map loaded successfully.')

    def load_sensor_config(self, sensor_type):
        """
        Loads sensor configuration from a JSON file.

        Args:
            sensor_type (str): The type of sensor ('camera', 'radar', 'ultrasonic').

        Returns:
            dict: The configuration for the specified sensor type.
        """
        with open(SENSOR_CONFIG_PATH[sensor_type], 'r') as file:
            return json.load(file)

    def setup_sensors(self):
        """
        Sets up sensors based on predefined configurations.
        """
        camera_configs = self.load_sensor_config("camera")
        for config in camera_configs:
            camera_sensor = CameraSensor(self.world, self.vehicle, config)
            if camera_sensor.setup():
                self.sensors_list.append(camera_sensor.sensor)
                logging.info(f"Camera sensor {camera_sensor.sensor.attributes['role_name']} setup completed.")

        radar_configs = self.load_sensor_config("radar")
        for config in radar_configs:
            radar_sensor = RadarSensor(self.world, self.vehicle, config)
            if radar_sensor.setup():
                self.sensors_list.append(radar_sensor.sensor)
                logging.info(f"Radar sensor {radar_sensor.sensor.attributes['role_name']} setup completed.")

        ultrasonic_configs = self.load_sensor_config("ultrasonic")
        for config in ultrasonic_configs:
            ultrasonic_sensor = UltrasonicSensor(self.world, self.vehicle, config)
            if ultrasonic_sensor.setup():
                self.sensors_list.append(ultrasonic_sensor.sensor)
                logging.info(f"Ultrasonic sensor {ultrasonic_sensor.sensor.attributes['role_name']} setup completed.")

    def setup_vehicle(self):
        """
        Sets up a vehicle in the simulation at a random spawn point.
        """
        vehicle_bp = self.blueprint_library.find('vehicle.tesla.model3')
        spawn_point = random.choice(self.world.get_map().get_spawn_points())
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
        if self.autopilot:
            self.vehicle.set_autopilot(True)
            logging.info(f"Vehicle spawned: {self.vehicle.type_id}")
            logging.info("Autopilot enabled for the vehicle.")

            # Get Traffic Manager and set the speed limit
            traffic_manager = self.client.get_trafficmanager()
            traffic_manager.ignore_lights_percentage(self.vehicle, 0)
            traffic_manager.auto_lane_change(self.vehicle, True)
            traffic_manager.vehicle_percentage_speed_difference(self.vehicle, 100 - (self.target_speed * 100 / 90))  # Scale according to default speed

    def set_spectator_camera(self):
        """
        Sets up a spectator camera on ego vehicle in the simulation.
        """
        spectator = self.world.get_spectator()
        transform = self.vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20, x=-10), transform.rotation))

    def update_spectator_camera(self):
        """
        Updates the spectator camera location with respect to the ego vehicle in the simulation.
        """
        spectator = self.world.get_spectator()
        transform = self.vehicle.get_transform()
        spectator.set_transform(carla.Transform(transform.location + carla.Location(z=20, x=-10), transform.rotation))

    def check_and_reposition_vehicle(self):
        """
        Checks for possible collisions between two ego vehicle and other vehicle actor.
        """
        vehicles = self.world.get_actors().filter('vehicle.*')
        ego_location = self.vehicle.get_location()

        for vehicle in vehicles:
            if vehicle.id != self.vehicle.id:
                other_location = vehicle.get_location()
                distance = ego_location.distance(other_location)

                if distance < 0.0:
                    logging.info(f"Vehicle {self.vehicle.id} is too close to NPC {vehicle.id}. Repositioning the vehicle.")
                    self.reposition_vehicle()
                    return True
        return False

    def reposition_vehicle(self):
        '''
            User can handle acording to his needs, 
            what s/he wants if there occurs a collision.

            Just a placeholder function for future development.
        '''
        self.vehicle.set_autopilot(False)
        nearby_spawn_points = self.world.get_map().get_spawn_points()
        safe_location = None

        for spawn_point in nearby_spawn_points:
            distance = self.vehicle.get_location().distance(spawn_point.location)
            if distance > 10.0:
                safe_location = spawn_point
                break

        if safe_location:
            self.vehicle.set_transform(safe_location)
            # self.vehicle.set_velocity(carla.Vector3D(0, 0, 0)) set_velocity() is not there in carla
            # It is just an example for user reference and further development
            logging.info(f"Vehicle repositioned to {safe_location.location}. Resuming autopilot.")
            self.vehicle.set_autopilot(True)

    def begin_data_acquisition(self, skip_frames=30, capture_interval=45, frames_to_capture=5):
        """
        Begins data collection for a specified number of frames at set intervals.

        Args:
            skip_frames (int): Number of initial frames to skip for stabilization.
            capture_interval (int): Interval between frame captures to reduce data redundancy.
            frames_to_capture (int): Total number of frames to capture.
        """
        with CarlaSyncMode(self.world, *self.sensors_list, fps=30) as sync_mode:
            for _ in range(skip_frames):
                sync_mode.tick_no_data()

            captured_frames = 0
            while captured_frames < frames_to_capture:
                if self.check_and_reposition_vehicle():
                    # Not Implemented
                    break

                for _ in range(capture_interval):
                    sync_mode.tick_no_data()

                sensor_data = sync_mode.tick(timeout=2.0)

                self.update_spectator_camera()

                for i, sensor in enumerate(self.sensors_list):
                    data = sensor_data[i + 1]
                    role_name = sensor.attributes.get('role_name', '')

                    if isinstance(data, carla.Image):
                        self.data_processor.process_camera_data(data, sensor.id, role_name, captured_frames)

                    elif isinstance(data, carla.RadarMeasurement):
                        if i == 8:
                            self.data_processor.process_radar_data(data, sensor.id, role_name, captured_frames)
                        else:
                            self.data_processor.process_ultrasonic_data(data, sensor.id, role_name, captured_frames)
                    else:
                        logging.error(f"Unexpected data type: {type(data)}")

                captured_frames += 1
                logging.info(f'Captured frame {captured_frames}/{frames_to_capture}')

        self.cleanup()

    def cleanup(self):
        """
        Cleans up the simulation by destroying the sensors and the vehicle.
        """
        logging.info("Removing all sensors from the simulation.")
        for sensor in self.sensors_list:
            if sensor.is_alive:
                sensor.destroy()
        self.sensors_list = []

        if self.vehicle:
            logging.info(f"Destroying vehicle {self.vehicle.type_id}")
            self.vehicle.destroy()
            self.vehicle = None

    def spawn_npcs(self, number_of_vehicles, number_of_walkers):
        """
        Spawns NPCs (vehicles and walkers) in the simulation.

        Args:
            number_of_vehicles (int): Number of vehicles to spawn.
            number_of_walkers (int): Number of walkers to spawn.
        """
        self.NPC = NPCClass()
        self.vehicles_list, _ = self.NPC.create_npcs(number_of_vehicles, number_of_walkers)
        logging.info(f"Spawned {number_of_vehicles} vehicles and {number_of_walkers} walkers.")

    def remove_npcs(self):
        """
        Removes all NPCs (vehicles and walkers) from the simulation.
        """
        logging.info("Destroying all NPC vehicles and walkers.")
        if hasattr(self, 'NPC') and self.NPC:
            self.NPC.remove_npcs()
            logging.info("All NPCs removed from the simulation.")

    def set_weather(self, weather_option):
        """
        Sets the weather in the simulation to a predefined configuration.

        Args:
            weather_option (list): The weather parameters to set.
        """
        weather = carla.WeatherParameters(*weather_option)
        self.world.set_weather(weather)
        logging.info("Weather set to new configuration.")

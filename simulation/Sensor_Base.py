import logging
import carla

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class SensorBase:
    def __init__(self, world, vehicle, sensor_config):
        self.world = world
        self.vehicle = vehicle
        self.sensor_config = sensor_config
        self.sensor = None

    def setup(self):
        raise NotImplementedError("Setup method needs to be implemented in subclasses.")

    def spawn_sensor(self, blueprint, transform, role_name):
        try:
            blueprint.set_attribute('role_name', role_name)
            self.sensor = self.world.spawn_actor(blueprint, transform, attach_to=self.vehicle)
            return self.sensor
        except carla.CarlaException as e:
            logging.error(f'Failed to spawn sensor: {e}')
            return None

class CameraSensor(SensorBase):
    def setup(self):
        camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(self.sensor_config['resolution'][0]))
        camera_bp.set_attribute('image_size_y', str(self.sensor_config['resolution'][1]))
        camera_bp.set_attribute('fov', str(self.sensor_config['fov']))
        camera_bp.set_attribute('sensor_tick', str(self.sensor_config['sensor_tick']))

        transform = carla.Transform(
            carla.Location(x=self.sensor_config['position'][0],
                           y=self.sensor_config['position'][1],
                           z=self.sensor_config['position'][2]),
            carla.Rotation(pitch=self.sensor_config['rotation'][0],
                           yaw=self.sensor_config['rotation'][1],
                           roll=self.sensor_config['rotation'][2])
        )

        role_name = self.sensor_config['role_name']
        return self.spawn_sensor(camera_bp, transform, role_name)

class RadarSensor(SensorBase):
    def setup(self):
        radar_bp = self.world.get_blueprint_library().find('sensor.other.radar')
        radar_bp.set_attribute('horizontal_fov', str(self.sensor_config['horizontal_fov']))
        radar_bp.set_attribute('vertical_fov', str(self.sensor_config['vertical_fov']))
        radar_bp.set_attribute('range', str(self.sensor_config['range']))
        radar_bp.set_attribute('sensor_tick', str(self.sensor_config['sensor_tick']))

        transform = carla.Transform(
            carla.Location(x=self.sensor_config['position'][0],
                           y=self.sensor_config['position'][1],
                           z=self.sensor_config['position'][2]),
            carla.Rotation(pitch=self.sensor_config['rotation'][0],
                           yaw=self.sensor_config['rotation'][1],
                           roll=self.sensor_config['rotation'][2])
        )

        role_name = self.sensor_config['role_name']
        return self.spawn_sensor(radar_bp, transform, role_name)

class UltrasonicSensor(SensorBase):
    def setup(self):
        ultrasonic_bp = self.world.get_blueprint_library().find('sensor.other.radar')  # Using radar blueprint for ultrasonic simulation
        ultrasonic_bp.set_attribute('horizontal_fov', str(self.sensor_config['horizontal_fov']))
        ultrasonic_bp.set_attribute('vertical_fov', str(self.sensor_config['vertical_fov']))
        ultrasonic_bp.set_attribute('range', str(self.sensor_config['range']))
        ultrasonic_bp.set_attribute('sensor_tick', str(self.sensor_config['sensor_tick']))

        transform = carla.Transform(
            carla.Location(x=self.sensor_config['position'][0],
                           y=self.sensor_config['position'][1],
                           z=self.sensor_config['position'][2]),
            carla.Rotation(pitch=self.sensor_config['rotation'][0],
                           yaw=self.sensor_config['rotation'][1],
                           roll=self.sensor_config['rotation'][2])
        )

        role_name = self.sensor_config['role_name']
        return self.spawn_sensor(ultrasonic_bp, transform, role_name)

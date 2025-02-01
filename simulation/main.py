"""
python main.py collect
python main.py infer --duration 60  # Run inference for 60 seconds

"""
import glob
import os
import sys
import datetime
import random
import argparse
from carla_world import CarlaWorld
from YOLO_inference import YOLOInference, visualize_and_record

def main():
    """
    Main function to manage CARLA simulation for either data collection or inference.
    """
    parser = argparse.ArgumentParser(description="Manage CARLA simulation for data collection or inference.")
    parser.add_argument('mode', choices=['collect', 'infer'], help="Specify 'collect' for data collection or 'infer' for running inference.")
    parser.add_argument('--duration', type=int, default=30, help="Duration of video capture in seconds (default is 30 seconds).")
    args = parser.parse_args()

    # Initialize CarlaWorld object for the simulation environment
    cw = CarlaWorld()

    # Choose operation mode: Data collection or Inference
    if args.mode == 'collect':
        print("Starting data collection...")

        # Set weather for simulation
        # weather = [morning, midday, afternoon, default, almost_night]
        weather = cw.weather_options
        # cw.set_weather(random.choice(cw.weather_options))  # Set random weather for the simulation
        cw.set_weather(weather[0])  # Set out of 5 weathers defined

        # Spawn NPCs (vehicles, pedestrians) 
        cw.spawn_npcs(50, 60)  # Spawning 50 vehicles and 60 walkers

        # Start data acquisition
        cw.begin_data_acquisition()

        # Remove NPCs after data collection
        cw.remove_npcs()

    elif args.mode == 'infer':
        print("Starting inference...")

        # Initialize the YOLO Inference module
        inference_module = YOLOInference()  # Load the trained YOLO model for inference
        
        # Set weather for simulation (if needed)
        cw.set_weather(cw.weather_options[3])  # Set the desired weather for inference

        # Optionally spawn NPCs (According to your need for the inference)
        cw.spawn_npcs(50, 60)

        # Calculate max frames based on duration (duration * 30 FPS)
        max_frames = args.duration * 30

        # Perform real-time inference and record the output
        visualize_and_record(cw.world, cw.sensors_list, inference_module, max_frames)

        # Remove sensors and NPCs after inference
        cw.cleanup()
        cw.remove_npcs()

if __name__ == "__main__":
    main()

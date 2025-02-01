# YOLO-Based Real-Time Object Detection for Autonomous Driving in CARLA

This repository contains the source code and experimental setup for research project titled **"YOLO-Based Real-Time Object Detection for Autonomous Driving in CARLA"**.
---

## Project Overview

The project focuses on simulating an autonomous Tesla Model 3 in CARLA to facilitate multi-camera object detection in real-time. It integrates advanced sensor configurations, data collection pipeline, and machine learning models to address critical challenges in autonomous driving research.

---

## Key Features

- **Comprehensive Sensor Suite:** Simulates a Tesla Model 3 equipped with 21 sensors (8 RGB cameras, 1 radar, and 12 ultrasonic sensors) configured for 360-degree environmental coverage, with precise parameters such as Field of View (FOV), resolution, and range.
- **Synchronous Data Collection Pipeline:** Captures sensor data upto 30 FPS for data collection and 30 FPS for inference, organized into metadata-rich formats to support algorithm training and testing.
- **Custom Dataset Creation:** Leveraged Roboflow for labeling and creating an object detection dataset, focusing on vehicles, pedestrians, traffic lights, and traffic signs.
- **Real-Time Object Detection:** Integrated trained YOLO models into the CARLA simulation for multi-camera inference, with predictions visualized and recorded in dynamic 2x4 grid layouts.

---

## Achievements

1. **Autonomous Simulation Environment:** Developed a realistic Tesla Model 3 simulation in CARLA, including dynamic environmental interactions such as NPC vehicles, pedestrians, and variable weather conditions.
2. **Robust Data Collection:** Generated high-quality synthetic image dataset for 2D object detection, utilizing synchronized sensor outputs.
3. **Machine Learning Integration:** Successfully trained and implemented YOLO models (YOLOv8, YOLOv9, YOLOv10, and YOLO11) on custom dataset, enabling real-time inference at 30 FPS.
4. **Visual Output:** Enhanced object detection workflows by incorporating grid-based visualization and video recording for performance evaluation.
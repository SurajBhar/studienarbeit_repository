import cv2
import numpy as np
import torch
import carla
from ultralytics import YOLO
from set_synchronous_mode import CarlaSyncMode

class YOLOInference:
    """
    Handles the loading and inference using a pre-trained YOLOv8 model.
    """
    def __init__(self):
        """
        Initializes the YOLOv8 model from the specified path.
        """
        # Replace the path to the checkpoint with other trained models.
        model_path = "/home/client2/Desktop/Carla_Sim_Ego/checkpoints/Yolo11m/last.pt"
        self.model = YOLO(model_path)  # Load the pretrained model from the checkpoint

    def process_image(self, image):
        """
        Processes the image from CARLA sensor data for inference.

        Args:
            image (carla.Image): The image data from CARLA simulation.

        Returns:
            np.array: The processed image array ready for inference.
        """
        image.convert(carla.ColorConverter.Raw)
        img_array = np.frombuffer(image.raw_data, dtype=np.uint8)
        img_array = np.reshape(img_array, (image.height, image.width, 4))
        img_array = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_BGR2RGB)  # Convert to RGB
        
        # Resize the image to 640x640 (YOLO default size)
        img_array = cv2.resize(img_array, (640, 640))
        
        return img_array  # Return image directly for YOLO inference

    def perform_inference(self, img_array):
        """
        Performs object detection on the processed image and returns the results object.

        Args:
            img_array (np.array): The image array from CARLA simulation.

        Returns:
            Results: The YOLO model results containing bounding boxes, masks, etc.
        """
        # Convert the image to a PyTorch tensor and normalize it (YOLO expects values between 0 and 1)
        img_tensor = torch.from_numpy(img_array).float() / 255.0  # Normalize the image
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)  # Convert to [C, H, W] and add batch dimension
        
        # Print the shape of the tensor to ensure it has the correct dimensions
        print(f"Input tensor shape: {img_tensor.shape}")  # Should be [1, 3, 640, 640]

        # Run inference on the image tensor
        results = self.model(img_tensor)

        # Return the first Results object (since we only processed one image)
        return results[0]

    def process_results(self, results):
        """
        Processes the YOLO Results object and returns the image with bounding boxes.

        Args:
            results (Results): The YOLO Results object.

        Returns:
            np.array: The image with bounding boxes and labels drawn on it.
        """
        # Return the image with bounding boxes as a NumPy array
        img_with_boxes = results.plot()  # Get the image with bounding boxes
        return img_with_boxes

def visualize_and_record(world, sensors_list, inference_module, max_frames=900):
    """
    Continuously captures images, performs inference, visualizes the results, and records video.

    Args:
        world (carla.World): The CARLA world object.
        sensors_list (list): A list of camera sensors.
        inference_module (YOLOInference): The inference module instance.
        max_frames (int): The maximum number of frames to capture (default is 900 frames, equivalent to 30 seconds at 30 FPS).
    """
    output_width = 640 * 4  # 4 images horizontally, each 640 pixels wide
    output_height = 640 * 2  # 2 rows of images, each 640 pixels tall

    # Use the mp4v codec for .mp4 video files
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # H.264 codec for .mp4 videos
    out = cv2.VideoWriter('output_yolo11m_town_6_w3.mp4', fourcc, 30.0, (output_width, output_height))

    frame_count = 0  # Initialize frame counter

    try:
        with CarlaSyncMode(world, *sensors_list, fps=30) as sync_mode:
            while frame_count < max_frames:  # Stop after max_frames are captured
                sensor_data = sync_mode.tick(timeout=2.0)
                camera_images = []  # List to store processed images from 8 cameras

                # Process the camera images (ignore the first element and only take images)
                for i in range(1, 9):  # Index 1 to 8 for camera images
                    data = sensor_data[i]  # Get the camera image
                    if isinstance(data, carla.Image):
                        img_array = inference_module.process_image(data)  # Process the image
                        results = inference_module.perform_inference(img_array)  # Run inference
                        img_with_boxes = inference_module.process_results(results)  # Process results

                        camera_images.append(img_with_boxes)

                if len(camera_images) == 8:  # Ensure we have 8 images to display in a grid
                    # Stack images into a 2x4 grid (2 rows, 4 columns)
                    grid_img = np.vstack((np.hstack(camera_images[:4]), np.hstack(camera_images[4:])))
                    
                    # Display the image grid on the screen
                    cv2.imshow('Camera Grid', grid_img)
                    
                    # Use waitKey(1) to give time for window refresh, you can increase the delay if needed
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break  # Allow exiting with 'q'

                    # Write the grid frame to the video if valid
                    if grid_img is not None:
                        out.write(grid_img)  # Write the frame to the video

                frame_count += 1  # Increment the frame counter
    finally:
        out.release()  # Release the video writer
        cv2.destroyAllWindows()  # Close OpenCV windows

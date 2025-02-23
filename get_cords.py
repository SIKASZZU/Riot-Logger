import easyocr
import pyautogui
import numpy as np
import cv2
import mss
import time

# Step 1: Capture screenshot of Riot Client (you can adjust the area of interest)
def capture_riot_screenshot(region=None):
    with mss.mss() as sct:
        # Capture screenshot (optional region argument)
        screenshot = sct.grab(region or sct.monitors[1])  # Use monitor[1] for full screen
        screenshot_image = np.array(screenshot)
        # Convert screenshot to BGR format for OpenCV compatibility
        screenshot_image = cv2.cvtColor(screenshot_image, cv2.COLOR_BGRA2BGR)
        return screenshot_image


# Step 2: Use EasyOCR to extract text and coordinates
def extract_username_coordinates(image):
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English
    result = reader.readtext(image)  # Detect all the text regions

    username_coordinates = None

    for (bbox, text, prob) in result:
        if "username" in text.lower():  # Search for "username" in the detected text
            # Extract bounding box coordinates
            x_min, y_min = bbox[0]
            x_max, y_max = bbox[2]
            username_coordinates = (x_min, y_min, x_max, y_max)
            min, max = (x_min, y_min), (x_max, y_max)

    return min, max


# Main execution
def main():
    # Step 1: Capture screenshot of the Riot Client
    screenshot_image = capture_riot_screenshot()

    # Step 2: Use EasyOCR to find the username and get coordinates
    min, max = extract_username_coordinates(screenshot_image)

    min = (min[0].item(), min[1].item())
    max = (max[0].item(), max[1].item())

    print(min, max)

# Run the program
if __name__ == "__main__":
    main()

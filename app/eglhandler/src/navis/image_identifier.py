import cv2
import pyautogui
import time
import numpy as np

def get_mouse_coords(file_paths: str|list, duration: float, region: tuple=None) -> tuple:
    """ Searches for the specified image(s) on the screen
    and returns the coordinates of the first match found."""

    # Check if file_paths is a string, if it is convert it to a list
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    images: list = []
    for file in file_paths:
        image = cv2.imread(file)
        images.append(image)

    # Convert reference images to grayscale
    reference_grays = [cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) for image in images]

    # Get the start time
    start_time = time.time()

    while True:
        # Capture a screenshot of the screen
        if region is not None:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()

        screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        matches = []

        # Perform template matching for each reference image
        for i, reference_gray in enumerate(reference_grays):
            result = cv2.matchTemplate(screenshot_gray, reference_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # If the similarity score is above a certain threshold, consider it a match
            threshold = 0.90
            if max_val > threshold:
                reference_height, reference_width = reference_gray.shape
                center_x = max_loc[0] + reference_width // 2
                center_y = max_loc[1] + reference_height // 2

                matches.append((center_x, center_y))

        if matches:
            # Return the first match found
            return matches[0]
        
        # Check if the specified duration has elapsed
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration:
            break
    
    # Return None if no matches found within the timeframe
    return None
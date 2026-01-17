import cv2
import numpy as np
import io

def apply_watercolor_style(image_bytes):
    """
    Applies the complex, multi-stage watercolor effect to an image.
    Takes raw image bytes and returns processed image bytes (PNG format).
    """
    try:
        # Read the image bytes into a numpy array for OpenCV
        image_np = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image data.")

        # --- GLOBAL SCALING ---
        # Calculate a scale factor to resize the image based on a target total pixel count (3000)
        scale = float(3000) / (img.shape[0] + img.shape[1])
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
        
        # --- Part 1: Soft Color Base (Simulating Wet Paint) ---
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Adjust the Value (V) channel for brighter, more vivid colors
        adjust_v = (img_hsv[:, :, 2].astype("uint") + 5) * 3
        adjust_v = ((adjust_v > 255) * 255 + (adjust_v <= 255) * adjust_v).astype("uint8")
        img_hsv[:, :, 2] = adjust_v

        # Apply strong Gaussian blur for diffusion
        img_soft = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
        img_soft = cv2.GaussianBlur(img_soft, (51, 51), 0)

        # --- Part 2: Detail/Line Extraction (Simulating Pencil Sketch) ---
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.equalizeHist(img_gray)
        invert = cv2.bitwise_not(img_gray)
        blur = cv2.GaussianBlur(invert, (21, 21), 0)
        invertedblur = cv2.bitwise_not(blur)

        # Create the sketch layer using division blend
        sketch = cv2.divide(img_gray, invertedblur, scale=265.0)
        sketch = cv2.merge([sketch, sketch, sketch])

        # --- Part 3: Blending ---
        # Blend sketch (detail) with soft color base (wet paint)
        img_water = ((sketch / 255.0) * img_soft).astype("uint8")
        processed_img = img_water

        # Convert the processed OpenCV image (BGR) back to a PNG byte stream
        is_success, buffer = cv2.imencode(".png", processed_img)
        if not is_success:
            raise Exception("Failed to encode processed image to PNG.")

        return buffer.tobytes()

    except Exception as e:
        print(f"Error in watercolor processing: {e}")
        # On error, return the original bytes for graceful failure
        return image_bytes

import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def apply_cartoon_filter(image_bytes: bytes, style: str) -> bytes:
    """
    Applies a classic image processing filter (e.g., Cartoon, Sketch, Oil)
    to the image based on the selected style.
    """
    
    # 1. Convert bytes to OpenCV image (BGR format)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image bytes.")
    
    # Initialize result image
    cartoon_img = img

    # --- Filter Logic ---

    if style == "Classic Cartoon":
        
        # 1. Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Smooth the Grayscale image to prepare for edge detection
        # Median Blur is good for noise removal without destroying edges completely
        blurred = cv2.medianBlur(gray, 5) 
        
        # 3. Detect Edges using Adaptive Thresholding (creates the black outlines)
        edges = cv2.adaptiveThreshold(
            blurred, 
            255,                                  # Max value to use
            cv2.ADAPTIVE_THRESH_MEAN_C,           # Method to calculate threshold
            cv2.THRESH_BINARY,                    # Type of thresholding
            9,                                    # Block size (neighborhood size)
            9                                     # Constant subtracted from mean
        )
        
        # 4. Smooth the Color image (Color Quantization/Simplification)
        # Bilateral filter smooths colors while preserving defined edges
        color_smoothed = cv2.bilateralFilter(img, 9, 300, 300) 
        
        # 5. Combine the smoothed color image with the black edge mask
        cartoon_img = cv2.bitwise_and(color_smoothed, color_smoothed, mask=edges)
        

    elif style == "Pencil Sketch":
        # Placeholder for Pencil Sketch logic
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blurred = cv2.GaussianBlur(inverted, (15, 15), 0)
        final_sketch = cv2.divide(gray, 255 - blurred, scale=256)
        cartoon_img = cv2.cvtColor(final_sketch, cv2.COLOR_GRAY2BGR)


    elif style == "Oil Painting":
        # Placeholder for Oil Painting logic
        cartoon_img = cv2.xphoto.oilPainting(img, 7, 1)




    # 6. Convert the final result from OpenCV (BGR) to RGB for PIL/Streamlit
    result_img_rgb = cv2.cvtColor(cartoon_img, cv2.COLOR_BGR2RGB)
    
    # 7. Convert the final NumPy array back to PNG bytes
    output_image_pil = Image.fromarray(result_img_rgb)
    output_buffer = BytesIO()
    output_image_pil.save(output_buffer, format="PNG")
    return output_buffer.getvalue()
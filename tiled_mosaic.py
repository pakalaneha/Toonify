import cv2
import numpy as np
import io

def apply_tiled_mosaic_style(image_bytes):
    """
    Applies a clean Geometric Mosaic / Tiled Art effect.
    The image is divided into uniform squares (tiles), and each tile is 
    filled with its single average color, creating a simplified, modern look.
    Takes raw image bytes and returns processed image bytes (PNG format).
    """
    # --- Parameters for Tiled Mosaic Look ---
    # TILE_SIZE: Defines the height and width of the square tiles (e.g., 16x16 pixels).
    # A larger number means fewer, larger tiles and more simplification.
    TILE_SIZE = 18 
    
    try:
        # 1. Load Image
        image_np = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image data.")
            
        h, w, c = img.shape
        
        # --- Part 1: Color Simplification by Averaging ---
        
        # Create a blank canvas for the processed image
        processed_img = np.zeros_like(img)
        
        # Iterate through the image, block by block (the "tiles")
        for i in range(0, h, TILE_SIZE):
            for j in range(0, w, TILE_SIZE):
                # Define the current tile's boundaries
                i_end = min(i + TILE_SIZE, h)
                j_end = min(j + TILE_SIZE, w)
                
                # Extract the tile region from the original image
                tile = img[i:i_end, j:j_end]
                
                # Calculate the average color of the tile
                # This gives one single color value (BGR) for the entire block
                mean_color = cv2.mean(tile)[:3]
                
                # Fill the corresponding block on the processed image with the mean color
                processed_img[i:i_end, j:j_end] = mean_color

        # --- Part 2: Optional Outline Enhancement ---
        # Add thin black lines between the tiles for definition (like grout)
        
        # Draw horizontal lines
        for i in range(TILE_SIZE, h, TILE_SIZE):
            cv2.line(processed_img, (0, i), (w, i), (0, 0, 0), 1)
        
        # Draw vertical lines
        for j in range(TILE_SIZE, w, TILE_SIZE):
            cv2.line(processed_img, (j, 0), (j, h), (0, 0, 0), 1)

        # 3. Finalize and Return Bytes
        is_success, buffer = cv2.imencode(".png", processed_img)
        if not is_success:
            raise Exception("Failed to encode processed image to PNG.")

        return buffer.tobytes()

    except Exception as e:
        print(f"Error in Tiled Mosaic processing: {e}")
        return image_bytes
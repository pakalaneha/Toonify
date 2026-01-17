import cv2
import numpy as np
import io
import random

def apply_low_poly_style(image_bytes):
    """
    Applies the Low-Poly Art style using Delaunay Triangulation.
    This breaks the image into large, color-averaged triangles.
    Takes raw image bytes and returns processed image bytes (PNG format).
    """
    # Parameters for the Low-Poly look
    NUM_POINTS = 500  # Number of random points to use for triangulation (fewer points = larger triangles)
    
    try:
        # Read the image bytes into a numpy array for OpenCV
        image_np = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image data.")

        h, w, c = img.shape

        # 1. Define the Delaunay Subdivisions (Grid)
        # Create a bounding rectangle for the triangulation
        rect = (0, 0, w, h)
        # Create the Delaunay Subdiv2D object
        subdiv = cv2.Subdiv2D(rect)

        # 2. Add Random Points for Triangulation
        # Include corner points and a few edge points to ensure coverage
        points = [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]
        for _ in range(NUM_POINTS):
            points.append((random.randint(0, w-1), random.randint(0, h-1)))

        for p in points:
            subdiv.insert(p)

        # 3. Process Triangles and Color Averaging
        processed_img = np.zeros_like(img)
        
        # Get the list of all triangles from the triangulation
        triangle_list = subdiv.getTriangleList()

        for t in triangle_list:
            # Get the three vertices of the triangle
            v1 = (int(t[0]), int(t[1]))
            v2 = (int(t[2]), int(t[3]))
            v3 = (int(t[4]), int(t[5]))

            # Create a contour from the vertices
            contour = np.array([v1, v2, v3], dtype=np.int32)
            
            # Create a mask for the current triangle
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask, [contour], 0, 255, -1)

            # Calculate the average color of the original image inside the triangle mask
            if cv2.countNonZero(mask) > 0:
                mean_color = cv2.mean(img, mask=mask)[:3]
            else:
                # If the triangle is invalid/too small, default to black or average
                mean_color = (0, 0, 0)

            # Fill the triangle on the processed image with the average color
            cv2.drawContours(processed_img, [contour], 0, mean_color, -1)
            
            # Optional: Draw faint black outlines for definition (comment out for smoother look)
            cv2.drawContours(processed_img, [contour], 0, (0, 0, 0), 1)

        # Convert the processed OpenCV image (BGR) back to a PNG byte stream
        is_success, buffer = cv2.imencode(".png", processed_img)
        if not is_success:
            raise Exception("Failed to encode processed image to PNG.")

        return buffer.tobytes()

    except Exception as e:
        print(f"Error in Low-Poly processing: {e}")
        # On error, return the original bytes for graceful failure
        return image_bytes
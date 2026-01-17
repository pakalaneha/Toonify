import sys
import random
import time
import numpy as np
from matplotlib import pyplot as plt
from skimage import draw
from math import ceil, pi

MEASURE_MIN_TIME = False
BRUSHES = 50

def showImage(image):
    plt.imshow(image)
    plt.show()

def process(inputImage, brushSize, expressionLevel):
    start = time.time()
    
    brushSizeInt = int(brushSize)
    expressionSize = brushSize * expressionLevel
    margin = int(expressionSize * 2)
    halfBrushSizeInt = brushSizeInt // 2
    
    # --- ENHANCEMENT FOR CLARITY/DENSITY ---
    # Reduce the step size to increase the number of strokes applied, 
    # ensuring the canvas is fully covered for an HD look.
    step_size = max(1, brushSizeInt // 2) 
    # ----------------------------------------
    
    if inputImage.shape[0] <= 2 * margin or inputImage.shape[1] <= 2 * margin:
        print("Image too small for brush size, returning original.")
        return inputImage, 0.0

    # Pre-calculate a set of brushes (ellipses) centered at halfBrushSizeInt
    brushes = [draw.ellipse(halfBrushSizeInt, halfBrushSizeInt, 
                            brushSize, 
                            random.randint(brushSizeInt, int(expressionSize)), 
                            rotation=random.random() * pi) 
               for _ in range(BRUSHES)]

    # Initialize the result as black. Denser sampling handles the filling.
    result = np.zeros(inputImage.shape, dtype=np.uint8)

    # Iterate over the image using the reduced step size for higher density
    for x in range(margin, inputImage.shape[0] - margin, step_size):
        for y in range(margin, inputImage.shape[1] - margin, step_size):
            # Select a random brush style
            ellipseXs, ellipseYs = random.choice(brushes)
            
            # Clip the brush indices to ensure they fall within the image bounds
            final_Xs = x + ellipseXs
            final_Ys = y + ellipseYs
            
            # Mask out indices that fall outside the image bounds
            valid_indices = (final_Xs < inputImage.shape[0]) & \
                            (final_Ys < inputImage.shape[1]) & \
                            (final_Xs >= 0) & (final_Ys >= 0)
            
            # Apply the color of the current point (x, y) to the brush area
            result[final_Xs[valid_indices], final_Ys[valid_indices]] = inputImage[x, y]
    
    return result, time.time() - start
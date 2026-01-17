import torch
from PIL import Image, Image
from io import BytesIO

# Load model once at import time
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# Load the AnimeGAN2 generator model and face2paint function
try:
    # Ensure the model is loaded correctly
    model = torch.hub.load("bryandlee/animegan2-pytorch:main", "generator", device=device).eval()
    face2paint = torch.hub.load("bryandlee/animegan2-pytorch:main", "face2paint", device=device)
except Exception as e:
    # This block handles potential connection/model loading issues
    print(f"Error loading AnimeGAN2 model: {e}")
    model = None
    face2paint = None

def apply_anime_style(image_bytes: bytes, original_mime_type: str) -> bytes:
    """Apply AnimeGAN2 style, ensuring the output size matches the input size."""
    
    if model is None or face2paint is None:
        raise RuntimeError("AnimeGAN2 model failed to load. Cannot process image.")

    # Convert bytes to PIL
    input_image = Image.open(BytesIO(image_bytes)).convert("RGB")
    
    # --- FIX START: Capture Original Dimensions ---
    original_w, original_h = input_image.size
    # ---------------------------------------------
    
    # Apply AnimeGAN2 transformation
    # NOTE: The output_image here will likely have a different size (e.g., 512x512)
    output_image = face2paint(model, input_image, side_by_side=False)
    
    # --- FIX END: Resize Output to Match Input ---
    # Use the high-quality LANCZOS filter for best results when resizing
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        # Fallback for older Pillow versions
        resample_filter = Image.LANCZOS 
        
    final_output_image = output_image.resize(
        (original_w, original_h), 
        resample=resample_filter
    )
    # ---------------------------------------------
    
    # Convert final, correctly sized image back to bytes
    output_buffer = BytesIO()
    final_output_image.save(output_buffer, format="PNG")
    return output_buffer.getvalue()

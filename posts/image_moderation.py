import logging
from django.conf import settings
from PIL import Image
import io
import tempfile
import os
from nudenet import NudeDetector

logger = logging.getLogger(__name__)

nude_detector = NudeDetector()

def moderate_image(image_file):
    logger.info(f"Starting image moderation for file: {image_file.name}")
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file_path = temp_file.name
            
            # Save the uploaded file to the temporary file
            for chunk in image_file.chunks():
                temp_file.write(chunk)
        
        # Use NudeNet to detect inappropriate content
        result = nude_detector.detect(temp_file_path)
        
        # Open the image to get its dimensions
        with Image.open(temp_file_path) as img:
            image_area = img.width * img.height
        
        # Calculate the total area of detected inappropriate parts
        inappropriate_area = sum(box['box'][2] * box['box'][3] for box in result)
        inappropriate_percentage = (inappropriate_area / image_area) * 100
        
        is_safe = inappropriate_percentage < 1  # Consider safe if less than 1% of the image is flagged
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return {
            "is_safe": is_safe,
            "has_nudity": not is_safe,
            "is_explicit": not is_safe,
            "is_suggestive": not is_safe,
            "inappropriate_percentage": inappropriate_percentage,
            "detection_results": result
        }

    except Exception as e:
        logger.error(f"Error in moderate_image: {str(e)}", exc_info=True)
        raise
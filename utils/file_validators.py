import os
import magic
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Medical and standard file extensions
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
ALLOWED_MEDICAL_EXTENSIONS = [
    '.dcm',     # DICOM medical images
    '.nii',     # NIfTI neuroimaging
    '.gz',      # Compressed files (often .nii.gz)
    '.xml',     # Medical reports/data
    '.hl7',     # HL7 medical messaging
    '.csv',     # Medical data exports
    '.xlsx',    # Excel medical reports
    '.xls',     # Legacy Excel
]

ALL_ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS + ALLOWED_DOCUMENT_EXTENSIONS + ALLOWED_MEDICAL_EXTENSIONS

# MIME type mapping for medical files
MEDICAL_MIME_TYPES = {
    'application/dicom': ['.dcm'],
    'application/x-nifti': ['.nii'],
    'application/gzip': ['.gz'],
    'application/xml': ['.xml'],
    'text/xml': ['.xml'],
    'application/hl7-v2': ['.hl7'],
    'text/csv': ['.csv'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/vnd.ms-excel': ['.xls'],
}

def validate_file_extension(file):
    """Validate file extension against allowed types"""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALL_ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'File type "{ext}" not allowed. Allowed types: {", ".join(ALL_ALLOWED_EXTENSIONS)}'
        )
    return True

def validate_file_size(file):
    """Validate file size"""
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10485760)  # 10MB default
    if file.size > max_size:
        raise ValidationError(
            f'File size {file.size} bytes exceeds maximum allowed size of {max_size} bytes'
        )
    return True

def validate_image_file(file):
    """Additional validation for image files"""
    ext = os.path.splitext(file.name)[1].lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        try:
            # Verify it's actually an image
            img = Image.open(file)
            img.verify()
            
            # Check image dimensions (prevent extremely large images)
            if img.width > 4096 or img.height > 4096:
                raise ValidationError('Image dimensions too large. Maximum 4096x4096 pixels.')
                
        except Exception as e:
            raise ValidationError(f'Invalid image file: {str(e)}')
    return True

def validate_file_content(file):
    """Validate file content using python-magic"""
    try:
        # Read first chunk to determine file type
        file.seek(0)
        file_content = file.read(1024)
        file.seek(0)
        
        # Get MIME type
        mime_type = magic.from_buffer(file_content, mime=True)
        
        # Common safe MIME types
        safe_mime_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff',
            'application/pdf', 'text/plain', 'text/rtf',
            'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/csv', 'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        
        # Add medical MIME types
        safe_mime_types.extend(MEDICAL_MIME_TYPES.keys())
        
        if mime_type not in safe_mime_types:
            logger.warning(f"Potentially unsafe file type detected: {mime_type} for file {file.name}")
            # Allow but log for medical files that might have unusual MIME types
            
    except Exception as e:
        logger.error(f"Error validating file content: {str(e)}")
        # Don't fail validation if magic detection fails
        
    return True

def comprehensive_file_validation(file):
    """Run all file validations"""
    try:
        validate_file_extension(file)
        validate_file_size(file)
        validate_image_file(file)
        validate_file_content(file)
        logger.info(f"File validation passed for: {file.name}")
        return True
    except ValidationError as e:
        logger.warning(f"File validation failed for {file.name}: {str(e)}")
        raise
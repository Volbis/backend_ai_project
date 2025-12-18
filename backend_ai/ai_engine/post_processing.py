"""
Post-processing utilities for extracted data
Normalize, validate and clean extracted text and fields
"""

import re
from datetime import datetime
import logging

logger = logging.getLogger('ai_engine')


def normalize_date(date_str: str) -> str:
    """
    Normalize date strings to YYYY-MM-DD format
    Handles various input formats: DD/MM/YYYY, DD-MM-YYYY, etc.
    """
    if not date_str:
        return ""
    
    # Common date patterns
    patterns = [
        (r'(\d{2})[/-](\d{2})[/-](\d{4})', r'\3-\2-\1'),  # DD/MM/YYYY -> YYYY-MM-DD
        (r'(\d{4})[/-](\d{2})[/-](\d{2})', r'\1-\2-\3'),  # YYYY/MM/DD -> YYYY-MM-DD
        (r'(\d{2})[/-](\d{2})[/-](\d{2})', r'20\3-\2-\1'), # DD/MM/YY -> 20YY-MM-DD
    ]
    
    for pattern, replacement in patterns:
        match = re.search(pattern, date_str)
        if match:
            normalized = re.sub(pattern, replacement, date_str)
            try:
                # Validate the date is real
                datetime.strptime(normalized, '%Y-%m-%d')
                return normalized
            except ValueError:
                continue
    
    return date_str  # Return original if no pattern matches


def validate_date(date_str: str, max_future_days: int = 0) -> tuple:
    """
    Validate a date string
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        max_future_days: Maximum days in the future allowed (0 = no future dates)
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        
        if max_future_days == 0 and date_obj > today:
            return False, "Date is in the future"
        
        if date_obj.year < 1900:
            return False, "Date is too old (before 1900)"
        
        if date_obj.year > 2100:
            return False, "Date is too far in the future"
        
        return True, ""
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}"


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone numbers by removing spaces, dashes, and parentheses
    """
    if not phone:
        return ""
    
    # Remove common separators
    normalized = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # Add country code if missing (assuming French +33)
    if normalized.startswith('0') and len(normalized) == 10:
        normalized = '+33' + normalized[1:]
    
    return normalized


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text
    - Remove extra whitespace
    - Fix common OCR errors
    - Normalize special characters
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Common OCR error corrections
    ocr_corrections = {
        '0': 'O',  # Zero to letter O in certain contexts
        'l': 'I',  # lowercase L to uppercase I
        '|': 'I',  # pipe to I
    }
    
    # Apply corrections cautiously (only in word contexts)
    # This is a simple example, real implementation would be more sophisticated
    
    return text.strip()


def extract_field_by_pattern(text: str, field_name: str) -> str:
    """
    Extract specific fields using regex patterns
    
    Args:
        text: Full text content
        field_name: Type of field to extract (name, date_birth, id_number, etc.)
    
    Returns:
        Extracted field value or empty string
    """
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'(?:\+33|0)[1-9](?:[\s.-]*\d{2}){4}',
        'postal_code': r'\b\d{5}\b',
        'id_number': r'\b[A-Z0-9]{8,15}\b',
    }
    
    pattern = patterns.get(field_name)
    if not pattern:
        return ""
    
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def validate_extracted_fields(fields: dict) -> dict:
    """
    Validate and normalize all extracted fields
    
    Args:
        fields: Dictionary of extracted fields
    
    Returns:
        Dictionary with validation results and normalized values
    """
    validated = {
        'original': fields,
        'normalized': {},
        'errors': []
    }
    
    # Date fields
    for date_field in ['date_birth', 'date_issue', 'date_expiry']:
        if date_field in fields:
            original_date = fields[date_field]
            normalized_date = normalize_date(original_date)
            validated['normalized'][date_field] = normalized_date
            
            # Validate based on field type
            max_future = 3650 if date_field == 'date_expiry' else 0  # 10 years for expiry
            is_valid, error = validate_date(normalized_date, max_future)
            
            if not is_valid:
                validated['errors'].append(f"{date_field}: {error}")
    
    # Phone fields
    if 'phone' in fields:
        validated['normalized']['phone'] = normalize_phone_number(fields['phone'])
    
    # Text fields
    for text_field in ['name', 'address', 'city']:
        if text_field in fields:
            validated['normalized'][text_field] = clean_text(fields[text_field])
    
    return validated

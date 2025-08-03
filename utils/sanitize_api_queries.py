"""
Text processing utilities for API interactions.
"""

import re


def sanitize_api_queries(text: str, max_length: int = 200) -> str:
    """
    Clean text for API queries by removing problematic characters and formatting.
    
    Args:
        text: The text to clean
        max_length: Maximum allowed length (default 200)
        
    Returns:
        Cleaned text suitable for API queries
    """
    if not text:
        return text
    
    # Remove or replace problematic characters
    cleaned = text
    
    # Replace various quote types with simple quotes or remove them
    cleaned = cleaned.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    # Remove or replace other problematic special characters
    cleaned = cleaned.replace('&nbsp;', ' ')  # Non-breaking space
    cleaned = cleaned.replace('\u00a0', ' ')  # Unicode non-breaking space
    cleaned = cleaned.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')  # Line breaks and tabs
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Handle length limits
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + "..."
    
    # Remove or replace characters that commonly cause URL encoding issues
    problematic_chars = ['<', '>', '{', '}', '|', '\\', '^', '`', '[', ']']
    for char in problematic_chars:
        cleaned = cleaned.replace(char, '')
    
    # Replace colons which seem to cause OSF API issues
    cleaned = cleaned.replace(':', ' -')
    
    # Replace other potentially problematic punctuation
    cleaned = cleaned.replace(';', ',')  # Semicolons to commas
    cleaned = cleaned.replace('?', '')   # Remove question marks
    cleaned = cleaned.replace('!', '')   # Remove exclamation marks
    cleaned = cleaned.replace('#', '')   # Remove hashtags
    cleaned = cleaned.replace('%', '')   # Remove percent signs
    
    # Clean up any double spaces created by replacements
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned
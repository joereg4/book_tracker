import re
from html import unescape

def strip_html_tags(text):
    """Remove HTML tags from text while preserving content"""
    if not text:
        return ''
    
    # Convert HTML entities
    text = unescape(text)
    
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text 
# app/utils/text_processor.py

import re
import string
from difflib import SequenceMatcher

def clean_text(text):
    """
    Clean text by removing punctuation, extra spaces, and converting to lowercase
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def calculate_text_similarity(text1, text2):
    """
    Calculate similarity between two text strings using SequenceMatcher
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Clean texts
    clean_text1 = clean_text(text1)
    clean_text2 = clean_text(text2)
    
    # Calculate similarity
    return SequenceMatcher(None, clean_text1, clean_text2).ratio()

def extract_price_from_text(text):
    """
    Extract price from text
    
    Args:
        text (str): Text containing price
        
    Returns:
        float or None: Extracted price or None if not found
    """
    if not text:
        return None
    
    # Look for price patterns
    patterns = [
        r'\$(\d+\.?\d*)',  # $XX.XX
        r'(\d+\.?\d*)\s*dollars',  # XX.XX dollars
        r'(\d+\.?\d*)\s*USD',  # XX.XX USD
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                continue
    
    return None

def generate_negotiation_response(status, product_title, offered_price, actual_price, negotiation_round=1):
    """
    Generate a human-like negotiation response
    
    Args:
        status (str): Status of negotiation ('accepted', 'counter', 'rejected')
        product_title (str): Title of the product
        offered_price (float): Price offered by customer
        actual_price (float): Actual price of product
        negotiation_round (int): Current negotiation round
        
    Returns:
        str: Negotiation response
    """
    product_short_name = product_title.split(',')[0] if ',' in product_title else product_title[:30]
    
    if status == 'accepted':
        responses = [
            f"Deal! I can let you have the {product_short_name} for ${offered_price:.2f}.",
            f"You've got yourself a deal at ${offered_price:.2f} for the {product_short_name}.",
            f"I can accept your offer of ${offered_price:.2f} for the {product_short_name}. It's a good deal!"
        ]
        return responses[negotiation_round % len(responses)]
    
    elif status == 'counter':
        counter_price = (offered_price + actual_price) / 2
        discount_percentage = ((actual_price - counter_price) / actual_price) * 100
        
        responses = [
            f"I can't go as low as ${offered_price:.2f} for the {product_short_name}, but I could do ${counter_price:.2f} which is still {discount_percentage:.1f}% off the original price.",
            f"${offered_price:.2f} is a bit too low for the {product_short_name}. How about ${counter_price:.2f}? That's a fair price considering the quality.",
            f"I appreciate your offer of ${offered_price:.2f}, but the lowest I can go for the {product_short_name} is ${counter_price:.2f}. What do you think?"
        ]
        return responses[negotiation_round % len(responses)]
    
    else:  # rejected
        min_acceptable = actual_price * 0.8
        
        responses = [
            f"I'm sorry, but ${offered_price:.2f} is too low for the {product_short_name}. The price is already competitive at ${actual_price:.2f}.",
            f"I can't accept ${offered_price:.2f} for the {product_short_name}. The lowest I could possibly go would be closer to ${min_acceptable:.2f}.",
            f"Unfortunately, ${offered_price:.2f} doesn't work for the {product_short_name}. We need to be closer to ${min_acceptable:.2f} to make a deal."
        ]
        return responses[negotiation_round % len(responses)]

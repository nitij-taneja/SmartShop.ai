# app/utils/feature_extractor.py

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Feature extraction patterns
PATTERNS = {
    'ram': r'(\d+)\s*(?:GB|gb|G|g)\s*(?:RAM|ram|Ram)',
    'storage': r'(\d+)\s*(?:GB|gb|TB|tb|G|g|T|t)\s*(?:SSD|HDD|eMMC|storage|Storage)',
    'screen_size': r'(\d+\.?\d*)["-]\s*(?:inch|in|display|screen|IPS|LCD|LED|OLED|FHD|QHD|UHD)',
    'processor': r'(i\d-\d{4,}(?:[A-Z]*)?|[A-Z]\d-\d{4,}(?:[A-Z]*)?|Ryzen\s*\d|Snapdragon\s*\d+|Intel\s*[A-Za-z]*\s*\d+|AMD\s*[A-Za-z]*\s*\d+|Quad[\-\s]Core|Octa[\-\s]Core|Hexa[\-\s]Core)',
    'resolution': r'(\d+\s*[xX]\s*\d+|HD|FHD|QHD|UHD|4K|1080[pP]|720[pP]|2160[pP])',
    'battery': r'(\d+)\s*(?:mAh|Wh)\s*(?:battery|Battery)',
    'color': r'(?:Color|color|Colour|colour):\s*([A-Za-z]+)|(?:in|In)\s+([A-Za-z]+)(?:\s+color|\s+Color)',
    'bluetooth': r'(Bluetooth\s*\d+\.?\d*)',
    'waterproof': r'((?:IP|ip)\d{1,2}(?:X|\s*)?(?:\d{1,2})?|Water[\-\s]*(?:proof|resistant))',
    'wireless': r'(Wireless|wireless|Wi-Fi|wifi|WiFi)',
    'noise_cancelling': r'(Noise\s*(?:Cancelling|Cancellation|cancelling|cancellation))',
    'material': r'(?:made\s+of|Made\s+of|material:)\s+([A-Za-z]+)',
    'weight': r'(\d+\.?\d*)\s*(?:kg|g|Kg|KG|G|pounds|lbs|oz)',
}

def extract_features_from_title(title):
    """
    Extract product features from the title using regex patterns
    
    Args:
        title (str): Product title
        
    Returns:
        dict: Dictionary of extracted features
    """
    if not title:
        return {}
    
    features = {}
    
    # Extract features using patterns
    for feature_name, pattern in PATTERNS.items():
        match = re.search(pattern, title)
        if match:
            # Use the first group that matched
            for group in match.groups():
                if group:
                    features[feature_name] = group
                    break
    
    # Extract brand if not already in features
    words = word_tokenize(title)
    if words and len(words) > 0:
        # First word is often the brand
        potential_brand = words[0]
        if potential_brand not in stopwords.words('english'):
            features['brand'] = potential_brand
    
    # Extract category keywords
    category_keywords = {
        'electronics': ['wireless', 'bluetooth', 'earbuds', 'headphones', 'speaker', 'monitor', 'tv', 'camera'],
        'computers': ['laptop', 'computer', 'desktop', 'keyboard', 'mouse', 'webcam', 'processor', 'ram', 'ssd'],
        'home_kitchen': ['purifier', 'coffee', 'maker', 'cookware', 'kitchen', 'blender', 'mixer', 'toaster'],
        'beauty': ['moisturizer', 'cream', 'shampoo', 'conditioner', 'dryer', 'shaver', 'trimmer'],
        'toys': ['game', 'toy', 'puzzle', 'building', 'lego', 'doll', 'action figure'],
        'tools': ['drill', 'saw', 'hammer', 'screwdriver', 'wrench', 'tool', 'bulb', 'light'],
        'books': ['novel', 'fiction', 'nonfiction', 'book', 'author', 'story', 'series']
    }
    
    lower_title = title.lower()
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword.lower() in lower_title:
                features['category_keywords'] = features.get('category_keywords', []) + [keyword]
    
    if 'category_keywords' in features:
        features['category_keywords'] = list(set(features['category_keywords']))
    
    return features

def categorize_features(features):
    """
    Group features by type
    
    Args:
        features (dict): Dictionary of extracted features
        
    Returns:
        dict: Dictionary of categorized features
    """
    categories = {
        'technical_specs': ['ram', 'storage', 'processor', 'resolution', 'screen_size'],
        'physical_attributes': ['color', 'weight', 'material'],
        'connectivity': ['bluetooth', 'wireless'],
        'durability': ['waterproof', 'battery'],
        'audio': ['noise_cancelling'],
        'metadata': ['brand', 'category_keywords']
    }
    
    categorized = {}
    for category, feature_list in categories.items():
        category_features = {}
        for feature in feature_list:
            if feature in features:
                category_features[feature] = features[feature]
        
        if category_features:
            categorized[category] = category_features
    
    return categorized

def get_feature_importance_weights():
    """
    Return weights for different features to use in similarity calculations
    
    Returns:
        dict: Dictionary of feature weights
    """
    return {
        'ram': 0.8,
        'storage': 0.7,
        'processor': 0.9,
        'screen_size': 0.6,
        'resolution': 0.5,
        'battery': 0.4,
        'brand': 0.3,
        'color': 0.2,
        'bluetooth': 0.3,
        'waterproof': 0.3,
        'wireless': 0.3,
        'noise_cancelling': 0.4,
        'material': 0.3,
        'weight': 0.3,
        'category_keywords': 0.6
    }

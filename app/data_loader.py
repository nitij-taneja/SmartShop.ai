import os
import csv
import uuid
from typing import List, Dict, Any, Optional

from app.models.product import ProductModel
from app.utils.feature_extractor import extract_features_from_title

def load_all_products(data_dir: str = "../Data") -> List[ProductModel]:
    """
    Load all products from CSV files in the data directory
    
    Args:
        data_dir (str): Path to directory containing CSV files
        
    Returns:
        List[ProductModel]: List of product models
    """
    products = []
    
    # Get absolute path if relative path provided
    if not os.path.isabs(data_dir):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, data_dir)
    
    for file in os.listdir(data_dir):
        if file.startswith("amazon_") and file.endswith(".csv"):
            category = file.replace("amazon_", "").replace(".csv", "")
            file_path = os.path.join(data_dir, file)
            
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Generate a unique ID for the product
                    product_id = f"{category}_{uuid.uuid4().hex[:8]}"
                    
                    # Extract features from title
                    features = extract_features_from_title(row.get("Title", ""))
                    
                    # Parse numeric values
                    try:
                        price = float(row.get("Price", 0)) if row.get("Price") else None
                    except (ValueError, TypeError):
                        price = None
                        
                    try:
                        rating = float(row.get("Rating", 0)) if row.get("Rating") else None
                    except (ValueError, TypeError):
                        rating = None
                        
                    try:
                        reviews = int(row.get("Reviews", 0)) if row.get("Reviews") else 0
                    except (ValueError, TypeError):
                        reviews = 0
                    
                    # Create product model
                    product = ProductModel(
                        id=product_id,
                        title=row.get("Title", ""),
                        price=price,
                        rating=rating,
                        reviews=reviews,
                        brand=row.get("Brand") or features.get("brand"),
                        product_link=row.get("Product Link", ""),
                        category=category,
                        features=features,
                        image_url=None  # We don't have image URLs in the CSV
                    )
                    
                    products.append(product)
    
    return products

def get_product_by_id(product_id: str, products: List[ProductModel]) -> Optional[ProductModel]:
    """
    Get product by ID
    
    Args:
        product_id (str): Product ID
        products (List[ProductModel]): List of products
        
    Returns:
        Optional[ProductModel]: Product if found, None otherwise
    """
    for product in products:
        if product.id == product_id:
            return product
    return None

def filter_products_by_category(category: str, products: List[ProductModel]) -> List[ProductModel]:
    """
    Filter products by category
    
    Args:
        category (str): Category to filter by
        products (List[ProductModel]): List of products
        
    Returns:
        List[ProductModel]: Filtered products
    """
    return [p for p in products if p.category == category]

def filter_products_by_price_range(min_price: float, max_price: float, 
                                  products: List[ProductModel]) -> List[ProductModel]:
    """
    Filter products by price range
    
    Args:
        min_price (float): Minimum price
        max_price (float): Maximum price
        products (List[ProductModel]): List of products
        
    Returns:
        List[ProductModel]: Filtered products
    """
    return [p for p in products if p.price is not None and min_price <= p.price <= max_price]

def filter_products_by_rating(min_rating: float, products: List[ProductModel]) -> List[ProductModel]:
    """
    Filter products by minimum rating
    
    Args:
        min_rating (float): Minimum rating
        products (List[ProductModel]): List of products
        
    Returns:
        List[ProductModel]: Filtered products
    """
    return [p for p in products if p.rating is not None and p.rating >= min_rating]

def sort_products(products: List[ProductModel], sort_by: str = "rating", 
                 ascending: bool = False) -> List[ProductModel]:
    """
    Sort products by specified field
    
    Args:
        products (List[ProductModel]): List of products
        sort_by (str): Field to sort by (price, rating, reviews)
        ascending (bool): Sort in ascending order if True, descending if False
        
    Returns:
        List[ProductModel]: Sorted products
    """
    if sort_by == "price":
        # Handle None values in price
        return sorted(products, key=lambda p: p.price if p.price is not None else float('inf'), 
                     reverse=not ascending)
    elif sort_by == "rating":
        # Handle None values in rating
        return sorted(products, key=lambda p: p.rating if p.rating is not None else 0, 
                     reverse=not ascending)
    elif sort_by == "reviews":
        return sorted(products, key=lambda p: p.reviews, reverse=not ascending)
    else:
        return products  # No sorting if invalid sort_by

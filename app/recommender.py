from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from difflib import SequenceMatcher

from app.models.product import ProductModel
from app.utils.feature_extractor import extract_features_from_title, categorize_features, get_feature_importance_weights
from app.utils.text_processor import calculate_text_similarity, clean_text

class RecommendationEngine:
    """
    Enhanced recommendation engine with feature-based similarity and context awareness
    """
    
    def __init__(self, products: List[ProductModel]):
        """
        Initialize recommendation engine with products
        
        Args:
            products (List[ProductModel]): List of all products
        """
        self.products = products
        self.feature_weights = get_feature_importance_weights()
    
    def calculate_similarity_score(self, product1: ProductModel, product2: ProductModel) -> float:
        """
        Calculate similarity score between two products based on features and text
        
        Args:
            product1 (ProductModel): First product
            product2 (ProductModel): Second product
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Don't compare products from different categories
        if product1.category != product2.category:
            return 0.0
        
        # Calculate text similarity (30% weight)
        title_similarity = calculate_text_similarity(product1.title, product2.title) * 0.3
        
        # Calculate feature similarity (70% weight)
        feature_similarity = 0.0
        feature_count = 0
        
        # Compare common features
        for feature_name in set(product1.features.keys()) & set(product2.features.keys()):
            if feature_name in self.feature_weights:
                weight = self.feature_weights[feature_name]
                
                # Handle different feature types
                if feature_name == 'category_keywords':
                    # For list features, calculate Jaccard similarity
                    keywords1 = set(product1.features.get(feature_name, []))
                    keywords2 = set(product2.features.get(feature_name, []))
                    
                    if keywords1 and keywords2:
                        jaccard = len(keywords1 & keywords2) / len(keywords1 | keywords2)
                        feature_similarity += jaccard * weight
                        feature_count += 1
                else:
                    # For string/numeric features, calculate direct similarity
                    value1 = str(product1.features.get(feature_name, ''))
                    value2 = str(product2.features.get(feature_name, ''))
                    
                    if value1 and value2:
                        direct_sim = SequenceMatcher(None, value1, value2).ratio()
                        feature_similarity += direct_sim * weight
                        feature_count += 1
        
        # Normalize feature similarity
        if feature_count > 0:
            feature_similarity = feature_similarity / feature_count * 0.7
        
        # Combine similarities
        total_similarity = title_similarity + feature_similarity
        
        return total_similarity
    
    def find_similar_products(self, product: ProductModel, limit: int = 5) -> List[Tuple[ProductModel, float]]:
        """
        Find products similar to the given product
        
        Args:
            product (ProductModel): Reference product
            limit (int): Maximum number of similar products to return
            
        Returns:
            List[Tuple[ProductModel, float]]: List of similar products with similarity scores
        """
        similarities = []
        
        for other_product in self.products:
            # Skip the same product
            if other_product.id == product.id:
                continue
            
            # Calculate similarity
            similarity = self.calculate_similarity_score(product, other_product)
            
            if similarity > 0:
                similarities.append((other_product, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    def find_better_alternatives(self, product: ProductModel, limit: int = 3) -> List[Tuple[ProductModel, float]]:
        """
        Find better alternatives to the given product
        
        Args:
            product (ProductModel): Reference product
            limit (int): Maximum number of alternatives to return
            
        Returns:
            List[Tuple[ProductModel, float]]: List of better alternatives with similarity scores
        """
        # Find similar products
        similar_products = self.find_similar_products(product, limit=10)
        
        better_alternatives = []
        
        for other_product, similarity in similar_products:
            # Check if it's a better alternative
            is_better = False
            
            # Better rating
            if (product.rating is None and other_product.rating is not None) or \
               (product.rating is not None and other_product.rating is not None and other_product.rating > product.rating):
                is_better = True
            
            # More reviews (indicates more reliable product)
            if other_product.reviews > product.reviews * 1.5:
                is_better = True
            
            # Better features (more RAM, storage, etc.)
            if 'ram' in product.features and 'ram' in other_product.features:
                try:
                    ram1 = int(''.join(filter(str.isdigit, product.features['ram'])))
                    ram2 = int(''.join(filter(str.isdigit, other_product.features['ram'])))
                    if ram2 > ram1:
                        is_better = True
                except (ValueError, TypeError):
                    pass
            
            if 'storage' in product.features and 'storage' in other_product.features:
                try:
                    storage1 = int(''.join(filter(str.isdigit, product.features['storage'])))
                    storage2 = int(''.join(filter(str.isdigit, other_product.features['storage'])))
                    if storage2 > storage1:
                        is_better = True
                except (ValueError, TypeError):
                    pass
            
            # Only include if it's actually better
            if is_better:
                better_alternatives.append((other_product, similarity))
        
        # Sort by similarity (descending)
        better_alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return better_alternatives[:limit]
    
    def get_personalized_recommendations(self, viewed_products: List[ProductModel], 
                                        limit: int = 5) -> List[ProductModel]:
        """
        Get personalized recommendations based on viewed products
        
        Args:
            viewed_products (List[ProductModel]): Products the user has viewed
            limit (int): Maximum number of recommendations to return
            
        Returns:
            List[ProductModel]: List of recommended products
        """
        if not viewed_products:
            # Return some highly-rated products if no view history
            return sorted(
                [p for p in self.products if p.rating is not None], 
                key=lambda p: p.rating or 0, 
                reverse=True
            )[:limit]
        
        # Calculate similarity scores for all products
        product_scores = {}
        
        for product in self.products:
            # Skip products the user has already viewed
            if product.id in [p.id for p in viewed_products]:
                continue
            
            # Calculate similarity to each viewed product
            for viewed_product in viewed_products:
                similarity = self.calculate_similarity_score(product, viewed_product)
                
                # Accumulate similarity scores
                if product.id not in product_scores:
                    product_scores[product.id] = 0
                
                product_scores[product.id] += similarity
        
        # Get products with scores
        scored_products = [(p, product_scores.get(p.id, 0)) for p in self.products 
                          if p.id in product_scores]
        
        # Sort by score (descending)
        scored_products.sort(key=lambda x: x[1], reverse=True)
        
        # Return top products
        return [p for p, _ in scored_products[:limit]]

def find_relevant_products(query: str, products: List[ProductModel], limit: int = 5) -> List[ProductModel]:
    """
    Find products relevant to the given query
    
    Args:
        query (str): Search query
        products (List[ProductModel]): List of all products
        limit (int): Maximum number of products to return
        
    Returns:
        List[ProductModel]: List of relevant products
    """
    clean_query = clean_text(query)
    
    # Calculate relevance scores
    product_scores = []
    
    for product in products:
        # Calculate text similarity
        title_similarity = calculate_text_similarity(clean_query, product.title)
        
        # Extract features from query
        query_features = extract_features_from_title(query)
        
        # Calculate feature match score
        feature_match = 0
        for feature, value in query_features.items():
            if feature in product.features:
                feature_match += 1
        
        # Combine scores (70% title, 30% features)
        total_score = title_similarity * 0.7 + (feature_match / max(1, len(query_features))) * 0.3
        
        product_scores.append((product, total_score))
    
    # Sort by score (descending)
    product_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top products
    return [p for p, _ in product_scores[:limit]]

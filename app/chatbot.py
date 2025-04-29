import os
import json
from typing import List, Dict, Any, Optional

from together import Together
from app.models.product import ProductModel
from app.recommender import find_relevant_products
from app.utils.text_processor import clean_text

# Initialize Together AI client
TOGETHER_API_KEY = "615ffbede3a1cdc3a56335142cc4131c9228b69b5813713d3c1abe132dcb66a9"
client = Together(api_key=TOGETHER_API_KEY)

class ChatEngine:
    """
    Enhanced chat engine with Together AI integration and product awareness
    """
    
    def __init__(self, products: List[ProductModel]):
        """
        Initialize chat engine with products
        
        Args:
            products (List[ProductModel]): List of all products
        """
        self.products = products
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    
    def chat_with_together_ai(self, query: str, context: Optional[str] = None) -> str:
        """
        Generate response using Together AI
        
        Args:
            query (str): User query
            context (Optional[str]): Additional context
            
        Returns:
            str: Generated response
        """
        try:
            # Prepare prompt with context if available
            if context:
                prompt = f"Context: {context}\n\nUser: {query}\n\nAssistant:"
            else:
                prompt = f"User: {query}\n\nAssistant:"
            
            # Call Together AI API
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            # Fallback response in case of API failure
            return f"🤖 I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again later. Error: {str(e)}"
    
    def generate_product_aware_response(self, query: str) -> str:
        """
        Generate product-aware response
        
        Args:
            query (str): User query
            
        Returns:
            str: Generated response
        """
        # Find relevant products
        relevant_products = find_relevant_products(query, self.products, limit=5)
        
        if relevant_products:
            # Generate product list for context
            product_context = "Here are some relevant products:\n\n"
            
            for i, product in enumerate(relevant_products, 1):
                price_str = f"${product.price:.2f}" if product.price is not None else "Price not available"
                rating_str = f"{product.rating}/5" if product.rating is not None else "No rating"
                reviews_str = f"{product.reviews} reviews" if product.reviews else "No reviews"
                
                product_context += f"{i}. {product.title}\n"
                product_context += f"   - Price: {price_str}\n"
                product_context += f"   - Rating: {rating_str} ({reviews_str})\n"
                product_context += f"   - Category: {product.category}\n"
                
                # Add extracted features if available
                if product.features:
                    feature_str = ", ".join([f"{k}: {v}" for k, v in product.features.items() 
                                           if k != 'category_keywords'])
                    if feature_str:
                        product_context += f"   - Features: {feature_str}\n"
                
                product_context += "\n"
            
            # Generate response with product context
            return self.chat_with_together_ai(query, context=product_context)
        else:
            # No relevant products found, generate general response
            return self.chat_with_together_ai(query)
    
    def handle_shopping_query(self, query: str) -> Dict[str, Any]:
        """
        Handle shopping-related query
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: Response with products and message
        """
        # Find relevant products
        relevant_products = find_relevant_products(query, self.products, limit=5)
        
        if relevant_products:
            # Generate response with products
            return {
                "type": "product_results",
                "products": relevant_products,
                "message": f"I found {len(relevant_products)} products that match your query."
            }
        else:
            # No relevant products found
            return {
                "type": "text_response",
                "message": "I couldn't find any products matching your query. Could you try a different search term?"
            }
    
    def handle_general_query(self, query: str) -> Dict[str, Any]:
        """
        Handle general query
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, Any]: Response with message
        """
        # Generate response
        response = self.generate_product_aware_response(query)
        
        return {
            "type": "text_response",
            "message": response
        }

def chat_response(query: str, products: List[ProductModel]) -> str:
    """
    Generate chat response
    
    Args:
        query (str): User query
        products (List[ProductModel]): List of all products
        
    Returns:
        str: Generated response
    """
    chat_engine = ChatEngine(products)
    
    # Determine if it's a shopping query
    shopping_keywords = ["buy", "purchase", "shop", "find", "looking for", "search", "want", "need"]
    is_shopping_query = any(keyword in query.lower() for keyword in shopping_keywords)
    
    if is_shopping_query:
        result = chat_engine.handle_shopping_query(query)
        
        if result["type"] == "product_results":
            # Format product results as text
            response = f"🔍 {result['message']}\n\n"
            
            for i, product in enumerate(result["products"], 1):
                price_str = f"${product.price:.2f}" if product.price is not None else "Price not available"
                rating_str = f"⭐ {product.rating}" if product.rating is not None else ""
                reviews_str = f"({product.reviews} reviews)" if product.reviews else ""
                
                response += f"{i}. **{product.title}**\n"
                response += f"   💲 {price_str} {rating_str} {reviews_str}\n"
                response += f"   [View on Amazon]({product.product_link})\n\n"
            
            return response
        else:
            return result["message"]
    else:
        result = chat_engine.handle_general_query(query)
        return result["message"]

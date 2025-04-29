from typing import List, Dict, Any, Optional, Tuple
import random
from difflib import SequenceMatcher

from app.models.product import ProductModel, NegotiationHistory
from app.utils.text_processor import generate_negotiation_response
from app.utils.feature_extractor import get_feature_importance_weights

class NegotiationEngine:
    """
    Enhanced negotiation engine with multi-round capabilities and seller-side logic
    """
    
    def __init__(self, base_delivery_cost: float = 5.0, min_profit_percent: float = 15.0):
        """
        Initialize negotiation engine
        
        Args:
            base_delivery_cost (float): Base delivery cost
            min_profit_percent (float): Minimum profit percentage
        """
        self.base_delivery_cost = base_delivery_cost
        self.min_profit_percent = min_profit_percent
        self.negotiation_history: Dict[str, NegotiationHistory] = {}
    
    def calculate_min_acceptable_price(self, product: ProductModel) -> float:
        """
        Calculate minimum acceptable price based on product price, delivery cost, and minimum profit
        
        Args:
            product (ProductModel): Product to calculate minimum price for
            
        Returns:
            float: Minimum acceptable price
        """
        if product.price is None:
            return 0.0
        
        # Base cost is product price minus estimated profit margin (assuming 30% markup)
        estimated_base_cost = product.price / 1.3
        
        # Add delivery cost
        total_base = estimated_base_cost + self.base_delivery_cost
        
        # Add minimum profit
        min_profit = total_base * (self.min_profit_percent / 100)
        
        return round(total_base + min_profit, 2)
    
    def get_negotiation_round(self, product_id: str) -> int:
        """
        Get current negotiation round for a product
        
        Args:
            product_id (str): Product ID
            
        Returns:
            int: Current negotiation round (1-based)
        """
        if product_id not in self.negotiation_history:
            return 1
        
        return len(self.negotiation_history[product_id].negotiation_rounds) + 1
    
    def evaluate_offer(self, product: ProductModel, offered_price: float) -> Dict[str, Any]:
        """
        Evaluate customer offer and determine response
        
        Args:
            product (ProductModel): Product being negotiated
            offered_price (float): Price offered by customer
            
        Returns:
            Dict[str, Any]: Negotiation result with status and message
        """
        if product.price is None:
            return {
                "status": "error",
                "message": "Product price not available for negotiation."
            }
        
        product_id = product.id
        negotiation_round = self.get_negotiation_round(product_id)
        
        # Initialize negotiation history if not exists
        if product_id not in self.negotiation_history:
            self.negotiation_history[product_id] = NegotiationHistory(
                product_id=product_id,
                original_price=product.price
            )
        
        # Get minimum acceptable price
        min_acceptable = self.calculate_min_acceptable_price(product)
        
        # Record this offer
        self.negotiation_history[product_id].negotiation_rounds.append({
            "round": negotiation_round,
            "customer_offer": offered_price,
            "min_acceptable": min_acceptable
        })
        
        # Determine discount thresholds based on negotiation round
        # We become more flexible in later rounds
        if negotiation_round == 1:
            accept_threshold = 0.90  # Accept if >= 90% of original price
            counter_threshold = 0.80  # Counter if >= 80% of original price
        elif negotiation_round == 2:
            accept_threshold = 0.85  # Accept if >= 85% of original price
            counter_threshold = 0.75  # Counter if >= 75% of original price
        else:
            accept_threshold = 0.82  # Accept if >= 82% of original price
            counter_threshold = 0.70  # Counter if >= 70% of original price
        
        # Calculate thresholds
        accept_price = product.price * accept_threshold
        counter_price = product.price * counter_threshold
        
        # Evaluate offer
        if offered_price >= accept_price:
            # Accept the offer
            self.negotiation_history[product_id].status = "accepted"
            self.negotiation_history[product_id].final_price = offered_price
            
            return {
                "status": "accepted",
                "message": generate_negotiation_response(
                    "accepted", product.title, offered_price, product.price, negotiation_round
                ),
                "final_price": offered_price
            }
        
        elif offered_price >= counter_price and offered_price >= min_acceptable:
            # Counter offer
            # Calculate counter price - move 40% of the way from their offer to our original price
            counter_offer = offered_price + (product.price - offered_price) * 0.4
            counter_offer = round(counter_offer, 2)
            
            # Record counter offer
            self.negotiation_history[product_id].negotiation_rounds[-1]["counter_offer"] = counter_offer
            
            return {
                "status": "counter",
                "message": generate_negotiation_response(
                    "counter", product.title, offered_price, product.price, negotiation_round
                ),
                "counter_price": counter_offer
            }
        
        else:
            # Reject the offer
            if negotiation_round >= 3:
                # Final rejection after 3 rounds
                self.negotiation_history[product_id].status = "rejected"
            
            return {
                "status": "rejected",
                "message": generate_negotiation_response(
                    "rejected", product.title, offered_price, product.price, negotiation_round
                )
            }
    
    def get_negotiation_history(self, product_id: str) -> Optional[NegotiationHistory]:
        """
        Get negotiation history for a product
        
        Args:
            product_id (str): Product ID
            
        Returns:
            Optional[NegotiationHistory]: Negotiation history if exists, None otherwise
        """
        return self.negotiation_history.get(product_id)

def negotiate_offer(product: ProductModel, offered_price: float) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility
    
    Args:
        product (ProductModel): Product being negotiated
        offered_price (float): Price offered by customer
        
    Returns:
        Dict[str, Any]: Negotiation result with status and message
    """
    engine = NegotiationEngine()
    return engine.evaluate_offer(product, offered_price)

# app/models/product.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any

class ProductFeature(BaseModel):
    """Model for product features extracted from title"""
    name: str
    value: Union[str, int, float, List[str]]
    
class NegotiationHistory(BaseModel):
    """Model for tracking negotiation history"""
    product_id: str
    original_price: float
    negotiation_rounds: List[Dict[str, Any]] = []
    final_price: Optional[float] = None
    status: str = "pending"  # pending, accepted, rejected
    
class ProductModel(BaseModel):
    """Model for product data"""
    id: str = Field(..., description="Unique identifier for the product")
    title: str = Field(..., description="Product title")
    price: Optional[float] = Field(None, description="Product price")
    rating: Optional[float] = Field(None, description="Product rating")
    reviews: Optional[int] = Field(None, description="Number of product reviews")
    brand: Optional[str] = Field(None, description="Product brand")
    product_link: str = Field(..., description="Link to product page")
    category: str = Field(..., description="Product category")
    features: Dict[str, Any] = Field(default_factory=dict, description="Extracted product features")
    image_url: Optional[str] = Field(None, description="Product image URL")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "electronics_001",
                "title": "JBL Vibe Beam - True Wireless JBL Deep Bass Sound Earbuds, Bluetooth 5.2",
                "price": 49.99,
                "rating": 4.3,
                "reviews": 19881,
                "brand": "JBL",
                "product_link": "https://www.amazon.com/product/123",
                "category": "electronics",
                "features": {
                    "bluetooth": "5.2",
                    "category_keywords": ["wireless", "earbuds"],
                    "brand": "JBL"
                },
                "image_url": "https://example.com/image.jpg"
            }
        }

class CartItem(BaseModel):
    """Model for cart item"""
    product: ProductModel
    quantity: int = 1
    negotiated_price: Optional[float] = None
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this item"""
        price = self.negotiated_price if self.negotiated_price is not None else self.product.price
        if price is None:
            return 0.0
        return price * self.quantity

class Cart(BaseModel):
    """Model for shopping cart"""
    items: List[CartItem] = []
    
    @property
    def total(self) -> float:
        """Calculate total price for all items in cart"""
        return sum(item.total_price for item in self.items)
    
    @property
    def item_count(self) -> int:
        """Calculate total number of items in cart"""
        return sum(item.quantity for item in self.items)
    
    def add_item(self, product: ProductModel, quantity: int = 1, negotiated_price: Optional[float] = None) -> None:
        """Add item to cart"""
        # Check if product already in cart
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                if negotiated_price is not None:
                    item.negotiated_price = negotiated_price
                return
        
        # Add new item
        self.items.append(CartItem(
            product=product,
            quantity=quantity,
            negotiated_price=negotiated_price
        ))
    
    def remove_item(self, product_id: str) -> None:
        """Remove item from cart"""
        self.items = [item for item in self.items if item.product.id != product_id]
    
    def update_quantity(self, product_id: str, quantity: int) -> None:
        """Update quantity of item in cart"""
        for item in self.items:
            if item.product.id == product_id:
                item.quantity = quantity
                if item.quantity <= 0:
                    self.remove_item(product_id)
                return

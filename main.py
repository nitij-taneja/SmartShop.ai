from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.models.product import ProductModel, Cart, CartItem
from app.data_loader import load_all_products, filter_products_by_category
from app.chatbot import chat_response
from app.barter import NegotiationEngine
from app.recommender import RecommendationEngine, find_relevant_products

# Initialize FastAPI app
app = FastAPI(title="E-Commerce API", description="API for E-Commerce system with AI features")

# Enable CORS for frontend/backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load all products
products = load_all_products()

# Initialize engines
negotiation_engine = NegotiationEngine()
recommendation_engine = RecommendationEngine(products)

# Request & Response Models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

class NegotiationRequest(BaseModel):
    product_id: str
    offered_price: float

class NegotiationResponse(BaseModel):
    status: str
    message: str
    counter_price: Optional[float] = None
    final_price: Optional[float] = None

class RecommendationRequest(BaseModel):
    product_id: str
    limit: int = 5

class ProductResponse(BaseModel):
    id: str
    title: str
    price: Optional[float]
    rating: Optional[float]
    reviews: Optional[int]
    brand: Optional[str]
    product_link: str
    category: str
    features: Dict[str, Any]
    image_url: Optional[str]

# --- Routes ---

@app.get("/")
def home():
    return {"message": "🛒 E-Commerce API with AI features is live!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_req: ChatRequest):
    result = chat_response(chat_req.query, products)
    return {"response": result}

@app.get("/products", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: Optional[str] = "rating",
    limit: int = 20
):
    # Filter by category if provided
    if category:
        filtered_products = filter_products_by_category(category, products)
    else:
        filtered_products = products
    
    # Filter by price range if provided
    if min_price is not None and max_price is not None:
        filtered_products = [p for p in filtered_products if p.price is not None and min_price <= p.price <= max_price]
    
    # Filter by minimum rating if provided
    if min_rating is not None:
        filtered_products = [p for p in filtered_products if p.rating is not None and p.rating >= min_rating]
    
    # Sort products
    if sort_by == "price":
        filtered_products.sort(key=lambda p: p.price if p.price is not None else float('inf'))
    elif sort_by == "price_desc":
        filtered_products.sort(key=lambda p: p.price if p.price is not None else 0, reverse=True)
    elif sort_by == "rating":
        filtered_products.sort(key=lambda p: p.rating if p.rating is not None else 0, reverse=True)
    elif sort_by == "reviews":
        filtered_products.sort(key=lambda p: p.reviews, reverse=True)
    
    # Return limited number of products
    return filtered_products[:limit]

@app.get("/product/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    # Find product by ID
    product = next((p for p in products if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@app.post("/negotiate", response_model=NegotiationResponse)
def negotiate(req: NegotiationRequest):
    # Find product by ID
    product = next((p for p in products if p.id == req.product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Evaluate offer
    result = negotiation_engine.evaluate_offer(product, req.offered_price)
    
    return result

@app.get("/recommendations/similar/{product_id}", response_model=List[ProductResponse])
def get_similar_products(product_id: str, limit: int = 5):
    # Find product by ID
    product = next((p for p in products if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get similar products
    similar_products = recommendation_engine.find_similar_products(product, limit=limit)
    
    return [p for p, _ in similar_products]

@app.get("/recommendations/better/{product_id}", response_model=List[ProductResponse])
def get_better_alternatives(product_id: str, limit: int = 3):
    # Find product by ID
    product = next((p for p in products if p.id == product_id), None)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get better alternatives
    better_alternatives = recommendation_engine.find_better_alternatives(product, limit=limit)
    
    return [p for p, _ in better_alternatives]

@app.post("/recommendations/personalized", response_model=List[ProductResponse])
def get_personalized_recommendations(product_ids: List[str], limit: int = 5):
    # Find products by IDs
    viewed_products = [p for p in products if p.id in product_ids]
    
    # Get personalized recommendations
    recommended_products = recommendation_engine.get_personalized_recommendations(viewed_products, limit=limit)
    
    return recommended_products

@app.get("/search", response_model=List[ProductResponse])
def search_products(query: str, limit: int = 10):
    # Find relevant products
    relevant_products = find_relevant_products(query, products, limit=limit)
    
    return relevant_products

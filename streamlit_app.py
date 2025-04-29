import streamlit as st
import requests
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import os
def has_price(product):
    return product.get("price") is not None


# Custom CSS for better styling
st.set_page_config(page_title="🛒 SmartShop AI", layout="wide")

st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: bold;
        color: #3D5AFE;
        text-align: center;
        margin-bottom: 25px;
    }
    .product-card {
        background-color: #fff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    .chat-box {
        background-color: #f0f4ff;
        color: #333;
        border-left: 4px solid #3D5AFE;
        padding: 12px 15px;
        border-radius: 5px;
        margin: 10px 0;
        white-space: pre-wrap;
    }
    .user-message {
        background-color: #e6f7ff;
        border-left: 4px solid #1890ff;
    }
    .bot-message {
        background-color: #f0f4ff;
        border-left: 4px solid #3D5AFE;
    }
    .price-tag {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2E7D32;
    }
    .rating-tag {
        color: #FF9800;
        font-weight: bold;
    }
    .category-badge {
        background-color: #E0E0E0;
        color: #424242;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 5px;
    }
    .negotiate-section {
        background-color: #f9f9ff;
        border: 1px solid #e0e0ff;
        border-radius: 8px;
        padding: 10px 15px;
        margin-top: 10px;
    }
    .cart-item {
        background-color: #f9f9ff;
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 10px;
        border-left: 4px solid #3D5AFE;
    }
    .cart-total {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E7D32;
        padding: 15px;
        background-color: #f0f4ff;
        border-radius: 8px;
        margin-top: 20px;
    }
    .section-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #333;
        margin: 20px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f0f0;
    }
    .recommendation-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #3D5AFE;
        margin: 15px 0 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint (adjust if needed)
API_URL = "http://localhost:8000"

# --- Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "viewed_products" not in st.session_state:
    st.session_state.viewed_products = []
if "negotiation_result" not in st.session_state:
    st.session_state.negotiation_result = {}

# --- Helper Functions ---
def get_products(category=None, min_price=None, max_price=None, min_rating=None, sort_by="rating", limit=20):
    """Get products from API"""
    params = {}
    if category:
        params["category"] = category
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if min_rating is not None:
        params["min_rating"] = min_rating
    if sort_by:
        params["sort_by"] = sort_by
    if limit:
        params["limit"] = limit
    
    try:
        response = requests.get(f"{API_URL}/products", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error loading products: {str(e)}")
        return []

def get_similar_products(product_id, limit=5):
    """Get similar products from API"""
    try:
        response = requests.get(f"{API_URL}/recommendations/similar/{product_id}?limit={limit}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error loading similar products: {str(e)}")
        return []

def get_better_alternatives(product_id, limit=3):
    """Get better alternatives from API"""
    try:
        response = requests.get(f"{API_URL}/recommendations/better/{product_id}?limit={limit}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error loading better alternatives: {str(e)}")
        return []

def get_personalized_recommendations(product_ids, limit=5):
    """Get personalized recommendations from API"""
    try:
        response = requests.post(
            f"{API_URL}/recommendations/personalized?limit={limit}",
            json=product_ids
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error loading personalized recommendations: {str(e)}")
        return []

def search_products(query, limit=10):
    """Search products from API"""
    try:
        response = requests.get(f"{API_URL}/search?query={query}&limit={limit}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error searching products: {str(e)}")
        return []

def negotiate_offer(product_id, offered_price):
    """Negotiate offer with API"""
    try:
        response = requests.post(
            f"{API_URL}/negotiate",
            json={"product_id": product_id, "offered_price": offered_price}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Error negotiating offer: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}"}

def chat_with_bot(query):
    """Chat with bot via API"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"query": query}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        st.error(f"⚠️ Error chatting with bot: {str(e)}")
        return "Sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."

def add_to_viewed_products(product):
    """Add product to viewed products list"""
    # Check if product already in viewed products
    if product["id"] not in [p["id"] for p in st.session_state.viewed_products]:
        st.session_state.viewed_products.append(product)
    
    # Keep only the last 10 viewed products
    if len(st.session_state.viewed_products) > 10:
        st.session_state.viewed_products = st.session_state.viewed_products[-10:]

def render_product_card(product, show_recommendations=False):
    """Render product card"""
    with st.container():
        st.markdown("<div class='product-card'>", unsafe_allow_html=True)
        
        cols = st.columns([1, 3])
        
        with cols[0]:
            # Product image (placeholder)
            st.image("https://via.placeholder.com/150", width=150)
        
        with cols[1]:
            # Product title and category
            st.markdown(f"<h3>{product['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<span class='category-badge'>{product['category'].replace('_', ' ').title()}</span>", unsafe_allow_html=True)
            
            # Product details
            details_cols = st.columns([1, 1, 2])
            
            with details_cols[0]:
                price = product.get("price")
                if price:
                    st.markdown(f"<div class='price-tag'>${price:.2f}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='price-tag'>Price not available</div>", unsafe_allow_html=True)
            
            with details_cols[1]:
                rating = product.get("rating")
                reviews = product.get("reviews", 0)
                if rating:
                    st.markdown(f"<div class='rating-tag'>⭐ {rating}/5</div>", unsafe_allow_html=True)
                    st.write(f"({reviews} reviews)")
                else:
                    st.write("No ratings yet")
            
            with details_cols[2]:
                # Features
                if product.get("features"):
                    features = []
                    for key, value in product["features"].items():
                        if key != "category_keywords":
                            features.append(f"{key}: {value}")
                    
                    if features:
                        st.markdown("**Key Features:**")
                        st.write(", ".join(features[:3]))
            
            # Action buttons
            action_cols = st.columns([1, 1, 2])
            
            with action_cols[0]:
                if st.button("Add to Cart", key=f"add_{product['id']}_{hash(product['title'])}"):
                    st.session_state.cart.append({
                        "product": product,
                        "quantity": 1,
                        "negotiated_price": None
                    })
                    st.success("✅ Added to cart")
                    st.rerun()
            
            with action_cols[1]:
                if st.button("View Details", key=f"view_{product['id']}"):
                    add_to_viewed_products(product)
                    st.session_state.current_product = product
                    st.rerun()
            
            with action_cols[2]:
                with st.expander("🧾 Negotiate Price"):
                    price = product.get("price")
                    if price:
                        offered_price = st.number_input(
                            "Your offer ($):",
                            min_value=price * 0.5,
                            max_value=price,
                            value=price * 0.9,
                            step=0.01,
                            key=f"offer_{product['id']}"
                        )
                        
                        if st.button("Submit Offer", key=f"negotiate_{product['id']}"):
                            result = negotiate_offer(product["id"], offered_price)
                            st.session_state.negotiation_result[product["id"]] = result
                            
                            if result["status"] == "accepted":
                                st.success(result["message"])
                                st.session_state.cart.append({
                                    "product": product,
                                    "quantity": 1,
                                    "negotiated_price": result.get("final_price")
                                })
                                st.rerun()
                            elif result["status"] == "counter":
                                st.info(result["message"])
                                st.write(f"Counter offer: ${result.get('counter_price', 0):.2f}")
                                
                                if st.button("Accept Counter", key=f"accept_counter_{product['id']}"):
                                    st.session_state.cart.append({
                                        "product": product,
                                        "quantity": 1,
                                        "negotiated_price": result.get("counter_price")
                                    })
                                    st.success("✅ Added to cart with negotiated price")
                                    st.rerun()
                            else:
                                st.error(result["message"])
                    else:
                        st.write("Price not available for negotiation")
        
        # Recommendations (if enabled)
        if show_recommendations:
            with st.expander("📊 Similar Products"):
                similar_products = [p for p in get_similar_products(product["id"], limit=5) if has_price(p)]

                
                if similar_products:
                    for similar in similar_products:
                        st.markdown(f"**{similar['title']}**")
                        cols = st.columns([1, 1])
                        with cols[0]:
                            price = similar.get("price")
                            if price:
                                st.write(f"Price: ${price:.2f}")
                            else:
                                st.write("Price not available")
                        with cols[1]:
                            if st.button("View", key=f"similar_{similar['id']}"):
                                add_to_viewed_products(similar)
                                st.session_state.current_product = similar
                                st.rerun()
                else:
                    st.write("No similar products found")
            
            with st.expander("⬆️ Better Alternatives"):
                better_alternatives = [p for p in get_better_alternatives(product["id"], limit=3) if has_price(p)]
                
                if better_alternatives:
                    for better in better_alternatives:
                        st.markdown(f"**{better['title']}**")
                        cols = st.columns([1, 1])
                        with cols[0]:
                            price = better.get("price")
                            if price:
                                st.write(f"Price: ${price:.2f}")
                            else:
                                st.write("Price not available")
                        with cols[1]:
                            if st.button("View", key=f"better_{better['id']}"):
                                add_to_viewed_products(better)
                                st.session_state.current_product = better
                                st.rerun()
                else:
                    st.write("No better alternatives found")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
st.markdown("<div class='main-title'>🛍️ SmartShop AI - Personalized Shopping</div>", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("Navigation")
    nav = st.radio("", ["Home", "Browse Products", "Search", "Chatbot", "Shopping Cart"])
    
    st.markdown("---")
    
    # Filters (for Browse and Search)
    if nav in ["Browse Products", "Search"]:
        st.subheader("Filters")
        
        categories = ["electronics", "computers", "home_kitchen", "beauty", "toys", "tools", "books"]
        selected_category = st.selectbox("Category", ["All"] + categories)
        
        price_range = st.slider("Price Range ($)", 0, 1000, (0, 1000))
        
        min_rating = st.slider("Minimum Rating", 1.0, 5.0, 4.0, 0.1)
        
        sort_options = {
            "Rating (High to Low)": "rating",
            "Price (Low to High)": "price",
            "Price (High to Low)": "price_desc",
            "Most Reviewed": "reviews"
        }
        sort_by = st.selectbox("Sort By", list(sort_options.keys()))
        
        # Convert filters to API parameters
        filter_params = {
            "min_price": price_range[0] if price_range[0] > 0 else None,
            "max_price": price_range[1] if price_range[1] < 1000 else None,
            "min_rating": min_rating,
            "sort_by": sort_options[sort_by],
            "limit": 20
        }
        
        if selected_category != "All":
            filter_params["category"] = selected_category

# --- Home Page ---
if nav == "Home":
    # Featured products
    st.markdown("<div class='section-title'>✨ Featured Products</div>", unsafe_allow_html=True)
    
    featured_products = [p for p in get_products(sort_by="rating", limit=10) if has_price(p)][:3]

    
    for product in featured_products:
        render_product_card(product)
    
    # Personalized recommendations
    if st.session_state.viewed_products:
        st.markdown("<div class='section-title'>🔮 Recommended For You</div>", unsafe_allow_html=True)
        
        product_ids = [p["id"] for p in st.session_state.viewed_products]
        recommended_products = [p for p in get_personalized_recommendations(product_ids, limit=10) if has_price(p)][:3]

        
        for product in recommended_products:
            render_product_card(product)
    
    # Categories showcase
    st.markdown("<div class='section-title'>🔍 Shop by Category</div>", unsafe_allow_html=True)
    
    categories = ["electronics", "computers", "home_kitchen", "beauty", "toys", "tools", "books"]
    
    for i in range(0, len(categories), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(categories):
                category = categories[i + j]
                with cols[j]:
                    st.markdown(f"### {category.replace('_', ' ').title()}")
                    
                    # Get top product for category
                    category_products = [p for p in get_products(category=category, limit=3) if has_price(p)]
                    
                    if category_products:
                        product = category_products[0]
                        st.markdown(f"**{product['title']}**")
                        
                        price = product.get("price")
                        if price:
                            st.markdown(f"<span class='price-tag'>${price:.2f}</span>", unsafe_allow_html=True)
                        
                        if st.button(f"Browse {category.replace('_', ' ').title()}", key=f"browse_{category}"):
                            st.session_state.browse_category = category
                            st.rerun()

# --- Browse Products ---
elif nav == "Browse Products":
    st.markdown("<div class='section-title'>🔎 Browse Products</div>", unsafe_allow_html=True)
    
    # Get category from session state if available
    if hasattr(st.session_state, "browse_category"):
        filter_params["category"] = st.session_state.browse_category
        # Clear the session state
        del st.session_state.browse_category
    
    # Get products with filters
    filtered_products = [p for p in get_products(**filter_params) if has_price(p)]
    
    if filtered_products:
        st.write(f"Showing {len(filtered_products)} products")
        
        for product in filtered_products:
            render_product_card(product)
    else:
        st.info("No products found matching your filters.")

# --- Search ---
elif nav == "Search":
    st.markdown("<div class='section-title'>🔍 Search Products</div>", unsafe_allow_html=True)
    
    search_query = st.text_input("Search for products:")
    
    if search_query:
        search_results = [p for p in search_products(search_query) if has_price(p)]

        
        if search_results:
            st.write(f"Found {len(search_results)} results for '{search_query}'")
            
            for product in search_results:
                render_product_card(product)
        else:
            st.info(f"No products found matching '{search_query}'")

# --- Chatbot ---
elif nav == "Chatbot":
    st.markdown("<div class='section-title'>💬 Chat with SmartBot</div>", unsafe_allow_html=True)
    
    # Display chat history
    for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
        st.markdown(f"<div class='chat-box user-message'><b>You:</b> {user_msg}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-box bot-message'><b>SmartBot:</b> {bot_msg}</div>", unsafe_allow_html=True)
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask me anything about products or shopping:", key="chat_input")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            # Get response from API
            bot_response = chat_with_bot(user_input)
            
            # Add to chat history
            st.session_state.chat_history.append((user_input, bot_response))
            
            # Rerun to update UI
            st.rerun()
    
    # Suggested questions
    st.markdown("### 💡 Try asking:")
    suggestion_cols = st.columns(2)
    
    suggestions = [
        "What are the best wireless earbuds?",
        "Can you recommend a laptop under $500?",
        "What's the difference between LCD and OLED?",
        "How do I choose the right power tools?"
    ]
    
    for i, suggestion in enumerate(suggestions):
        with suggestion_cols[i % 2]:
            if st.button(suggestion, key=f"suggestion_{i}"):
                # Get response from API
                bot_response = chat_with_bot(suggestion)
                
                # Add to chat history
                st.session_state.chat_history.append((suggestion, bot_response))
                
                # Rerun to update UI
                st.rerun()

# --- Shopping Cart ---
elif nav == "Shopping Cart":
    st.markdown("<div class='section-title'>🛒 Your Shopping Cart</div>", unsafe_allow_html=True)
    
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        
        if st.button("Browse Products"):
            st.rerun()
    else:
        # Calculate total
        total = 0
        
        # Display cart items
        for i, item in enumerate(st.session_state.cart):
            product = item["product"]
            quantity = item.get("quantity", 1)
            negotiated_price = item.get("negotiated_price")
            
            price = negotiated_price if negotiated_price is not None else product.get("price")
            item_total = price * quantity if price else 0
            total += item_total
            
            st.markdown("<div class='cart-item'>", unsafe_allow_html=True)
            
            cols = st.columns([3, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"**{product['title']}**")
                st.markdown(f"<span class='category-badge'>{product['category'].replace('_', ' ').title()}</span>", unsafe_allow_html=True)
            
            with cols[1]:
                if negotiated_price is not None:
                    st.markdown(f"<span class='price-tag'>${negotiated_price:.2f}</span> <small><s>${product.get('price', 0):.2f}</s></small>", unsafe_allow_html=True)
                    st.write("Negotiated price")
                else:
                    if price:
                        st.markdown(f"<span class='price-tag'>${price:.2f}</span>", unsafe_allow_html=True)
                    else:
                        st.write("Price not available")
            
            with cols[2]:
                new_quantity = st.number_input("Qty", min_value=1, max_value=10, value=quantity, key=f"qty_{i}")
                if new_quantity != quantity:
                    st.session_state.cart[i]["quantity"] = new_quantity
                    st.rerun()
            
            with cols[3]:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Display total
        st.markdown(f"<div class='cart-total'>Total: ${total:.2f}</div>", unsafe_allow_html=True)
        
        # Checkout button
        if st.button("🎉 Checkout (Simulated)"):
            # Save cart to file for demonstration
            with open("cart_checkout_log.json", "w", encoding='utf-8') as f:
                json.dump([{
                    "product_id": item["product"]["id"],
                    "title": item["product"]["title"],
                    "price": item["negotiated_price"] if item.get("negotiated_price") is not None else item["product"].get("price"),
                    "quantity": item.get("quantity", 1)
                } for item in st.session_state.cart], f, indent=2)
            
            st.success("✅ Order Placed! (Simulated)")
            st.balloons()
            
            # Clear cart
            st.session_state.cart = []
            
            # Rerun to update UI
            st.rerun()

# --- Product Detail View ---
if hasattr(st.session_state, "current_product"):
    product = st.session_state.current_product
    
    # Create a modal-like experience
    with st.container():
        st.markdown("<div class='section-title'>Product Details</div>", unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back"):
            del st.session_state.current_product
            st.rerun()
        
        # Render product with recommendations
        render_product_card(product, show_recommendations=True)
        
        # Clear current product if back button clicked
        if st.button("← Back to Shopping"):
            del st.session_state.current_product
            st.rerun()

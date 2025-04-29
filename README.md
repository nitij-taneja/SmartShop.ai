# SmartShop AI - E-Commerce Platform with AI Features

SmartShop AI is an advanced e-commerce platform that combines traditional shopping features with cutting-edge AI capabilities, including intelligent product recommendations, natural language chatbot assistance, and a unique price negotiation system.

## ✨ Features

- **AI-Powered Chatbot**: Get product recommendations and answers to shopping questions using natural language
- **Smart Bargaining System**: Negotiate prices with an AI shopkeeper that simulates real-world bargaining
- **Intelligent Recommendations**: Discover similar products and better alternatives based on product attributes
- **Feature-Based Search**: Find products based on specific features extracted from product titles
- **Responsive UI**: Enjoy a clean, modern shopping interface that works on all devices
- **Personalized Experience**: Receive recommendations based on your browsing history and preferences

## 🛠️ Technology Stack

- **Backend**: FastAPI for high-performance API endpoints
- **Frontend**: Streamlit for interactive user interface
- **AI/ML**: Together AI for natural language processing and chatbot capabilities
- **Data Processing**: Custom feature extraction and similarity algorithms
- **Data Storage**: CSV-based product database with rich metadata

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smartshop-ai.git
cd smartshop-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare data directory:
```bash
mkdir -p Data
# Copy CSV files to the Data directory
```

## 🏃‍♂️ Running the Application

### Start the Backend API

```bash
cd project
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Start the Frontend

In a new terminal:
```bash
cd project
streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

The application will be available at:
- Frontend: http://127.0.0.1:8501
- Backend API: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs

## 🧠 AI Features Explained

### Bargaining & Negotiation Engine

The system implements a sophisticated negotiation engine that:
- Calculates minimum acceptable prices based on base cost, delivery fees, and profit margins
- Supports multi-round negotiations with memory of previous offers
- Provides natural language responses that simulate real shopkeeper interactions
- Adapts negotiation strategy based on product category and customer behavior

### Recommendation Engine

The recommendation system uses:
- Feature extraction from product titles to identify key attributes (RAM, storage, screen size, etc.)
- Similarity calculations based on weighted feature matching
- Context-aware recommendations based on browsing history
- "Better alternatives" suggestions that highlight products with superior specifications

### Together AI Integration

The chatbot leverages Together AI to:
- Provide natural language responses to product queries
- Offer shopping assistance and product recommendations
- Handle fallback responses when specific product information isn't available
- Generate product-aware context for more relevant answers

## 📊 Project Structure

```
📁 Project Root/
│
├── 📁 app/
│   ├── 📁 utils/
│   │   ├── __init__.py
│   │   ├── feature_extractor.py  # For extracting product features from titles
│   │   └── text_processor.py     # For text processing utilities
│   │
│   ├── 📁 models/
│   │   ├── __init__.py
│   │   └── product.py            # Product data models
│   │
│   ├── chatbot.py                # Enhanced with Together AI integration
│   ├── barter.py                 # Enhanced negotiation engine
│   ├── recommender.py            # New recommendation engine
│   └── data_loader.py            # Enhanced data loader
│
├── 📁 Data/                      # Product data CSV files
│   ├── amazon_electronics.csv
│   ├── amazon_computers.csv
│   └── ...
│
├── main.py                       # FastAPI backend
├── streamlit_app.py              # Streamlit frontend
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```



## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Together AI](https://together.ai/) for providing the AI capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance backend
- [Streamlit](https://streamlit.io/) for the interactive frontend
- [Amazon](https://www.amazon.com/) for the product data used in development


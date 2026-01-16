# 🚀 AI Financial Planning Agent - Setup Guide

This guide will help you get the AI Financial Planning Agent running on your machine.

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Git**
- (Optional) **Docker & Docker Compose**
- (Optional) **Ollama** for local LLM

## 🎯 Quick Start Options

### Option 1: Docker (Easiest) ⭐

1. **Clone and configure**
```bash
cd ai-finance-agent
cp backend/.env.example backend/.env
```

2. **Add Gemini API Key**
Edit `backend/.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```
Get a free key at: https://ai.google.dev/

3. **Run with Docker**
```bash
docker-compose up --build
```

4. **Access the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Activate on Mac/Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

5. **Run backend**
```bash
uvicorn app.main:app --reload
```

Backend will run at http://localhost:8000

#### Frontend Setup

1. **Navigate to frontend (new terminal)**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

4. **Run frontend**
```bash
npm run dev
```

Frontend will run at http://localhost:5173

### Option 3: Local LLM with Ollama (Most Private)

1. **Install Ollama**
Visit https://ollama.ai and download for your OS

2. **Pull Llama model**
```bash
ollama pull llama3.1:8b
```

3. **Update backend .env**
```
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

4. **Start Ollama**
```bash
ollama serve
```

5. **Follow backend/frontend setup** from Option 2

## 🔑 Getting API Keys

### Gemini API (Free Tier)

1. Go to https://ai.google.dev/
2. Click "Get API key in Google AI Studio"
3. Create a new API key
4. Copy and paste into `backend/.env`

**Free tier includes:**
- 1500 requests per day
- Rate limit: 60 requests per minute
- More than enough for personal use!

## 📁 Project Structure

```
ai-finance-agent/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # AI agents (Budget, Goals, Health)
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # LLM and Vector services
│   │   └── main.py         # Main application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client
│   │   └── App.jsx         # Main app
│   └── package.json        # Node dependencies
├── data/                    # Financial knowledge base
├── docker-compose.yml       # Docker setup
└── README.md
```

## 🧪 Testing the Application

### 1. Test Budget Analysis

Upload a CSV file with transactions:
```csv
date,description,amount
2024-01-15,Grocery Store,-125.50
2024-01-16,Salary,3000.00
2024-01-17,Restaurant,-45.00
```

### 2. Create a Financial Goal

Try creating a goal like:
- Name: Emergency Fund
- Target: $10,000
- Current: $2,000
- Deadline: 2025-12-31

### 3. Calculate Health Score

Input your financial data:
- Monthly Income: $5,000
- Monthly Expenses: $3,500
- Savings: $15,000
- Debt: $5,000
- Emergency Fund: $9,000

### 4. Chat with AI

Ask questions like:
- "How can I save more money?"
- "What's the best way to pay off debt?"
- "Should I focus on saving or investing?"

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn app.main:app --port 8001
```

### Frontend build errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### ChromaDB errors
```bash
# Delete and reinitialize
rm -rf backend/chroma_db
# Restart backend - it will reinitialize automatically
```

### LLM connection errors
**For Gemini:**
- Check API key is correct in `.env`
- Verify you haven't exceeded free tier limits

**For Ollama:**
- Ensure Ollama is running: `ollama serve`
- Check model is downloaded: `ollama list`
- Verify model name matches `.env` config

## 🔒 Security Notes

- Never commit `.env` files to git
- Keep your API keys secret
- The free Gemini tier is for development/personal use
- For production, implement proper authentication

## 📊 Sample Data

Want to test without real data? Use our sample CSV:

```csv
date,description,amount,category
2024-01-01,Rent Payment,-1500,Housing
2024-01-05,Grocery Store,-234.56,Food & Dining
2024-01-08,Electric Bill,-89.23,Utilities
2024-01-10,Salary Deposit,4500,Income
2024-01-12,Amazon Purchase,-67.89,Shopping
2024-01-15,Gas Station,-45.00,Transportation
2024-01-18,Netflix Subscription,-15.99,Entertainment
2024-01-20,Gym Membership,-50.00,Personal Care
2024-01-22,Restaurant,-78.50,Food & Dining
2024-01-25,Car Insurance,-125.00,Transportation
```

## 🎓 Next Steps

1. ✅ Get basic app running
2. ✅ Upload sample transactions
3. ✅ Create your first financial goal
4. ✅ Calculate your health score
5. 🚀 Customize with your own data
6. 🌟 Star the repo if you find it useful!

## 🆘 Need Help?

- Check the [API documentation](http://localhost:8000/docs) when backend is running
- Review logs in terminal for error messages
- Open an issue on GitHub

Happy financial planning! 💰✨

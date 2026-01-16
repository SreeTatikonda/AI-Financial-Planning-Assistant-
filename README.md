# 🤖 AI Financial Planning Agent

A **zero-cost**, privacy-first AI-powered financial planning assistant that helps you manage budgets, track goals, and improve your financial health.

## ✨ Features

### Phase 1 (MVP - Current)
- 📊 **Budget Analysis**: Upload transactions, get intelligent categorization and insights
- 🎯 **Goal-Based Saving**: Set financial goals and get personalized savings plans
- 💯 **Financial Health Score**: Comprehensive assessment of your financial wellness

### Phase 2 (Coming Soon)
- 📈 Investment Portfolio Analysis
- 🏖️ Retirement Planning with Monte Carlo simulations
- 💰 Tax Optimization Recommendations

## 🏗️ Architecture

```
Frontend (React + Vite)
    ↓
Backend (FastAPI / Vercel Functions)
    ↓
LLM Layer (Gemini Flash 2.0 Free Tier / Local Ollama)
    ↓
Storage (Browser IndexedDB + SQLite)
```

## 🚀 Tech Stack

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Storage**: LocalForage (IndexedDB wrapper)
- **State**: React Context + Hooks

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite + SQLAlchemy
- **Vector DB**: ChromaDB (for financial knowledge)
- **LLM**: Gemini Flash 2.0 API (free tier) / Ollama (local)
- **Data Processing**: Pandas, NumPy

### AI/ML
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: Google Gemini Flash 2.0 (1500 requests/day free)
- **Local Option**: Llama 3.1 8B via Ollama

## 💸 Zero-Cost Deployment

### Option A: Serverless (Recommended)
- **Frontend**: Vercel (Free tier - unlimited bandwidth)
- **Backend**: Vercel Serverless Functions
- **Database**: Browser IndexedDB
- **LLM**: Gemini Flash 2.0 (free tier)
- **Cost**: $0/month ✅

### Option B: Fully Local
- Run everything on your machine using Docker Compose
- 100% private, no external dependencies
- Requires: Docker, Ollama, 8GB RAM

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.11+
- (Optional) Docker & Docker Compose
- (Optional) Ollama for local LLM

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-finance-agent.git
cd ai-finance-agent
```

2. **Set up Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env and add your Gemini API key (or leave blank for local Ollama)

# Run backend
uvicorn app.main:app --reload
```

3. **Set up Frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the app**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Setup (Recommended for Production)

```bash
# Build and run everything
docker-compose up --build

# Access at http://localhost:3000
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
# LLM Configuration
LLM_PROVIDER=gemini  # Options: gemini, ollama
GEMINI_API_KEY=your_api_key_here  # Get free at https://ai.google.dev
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_URL=sqlite:///./financial_agent.db

# Security
SECRET_KEY=your-secret-key-change-this
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_USE_LOCAL_STORAGE=true
```

## 📚 Project Structure

```
ai-finance-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementations
│   │   ├── api/             # FastAPI routes
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── tests/               # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API clients
│   │   └── utils/           # Frontend utilities
│   └── package.json
├── data/
│   ├── embeddings/          # Pre-computed embeddings
│   └── knowledge_base/      # Financial knowledge documents
├── docs/                    # Documentation
└── docker-compose.yml
```

## 🎯 Usage Examples

### 1. Budget Analysis
```python
# Upload CSV with columns: Date, Description, Amount, Category
# Get automatic categorization and insights
```

### 2. Set a Financial Goal
```python
POST /api/goals
{
  "name": "Emergency Fund",
  "target_amount": 10000,
  "deadline": "2025-12-31",
  "current_amount": 3000
}
```

### 3. Get Financial Health Score
```python
GET /api/health-score
# Returns 0-100 score with breakdown and recommendations
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with React, FastAPI, and Google Gemini
- Financial knowledge base curated from IRS guidelines, investopedia, and financial planning best practices
- Inspired by the need for accessible, privacy-first financial planning tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-finance-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-finance-agent/discussions)

## 🗺️ Roadmap

- [x] Budget Analysis
- [x] Goal Tracking
- [x] Financial Health Score
- [ ] Investment Portfolio Analysis
- [ ] Retirement Planning
- [ ] Tax Optimization
- [ ] Mobile App (React Native)
- [ ] Multi-currency Support
- [ ] Bank Account Integration (Plaid)

---

**Made with ❤️ for financial wellness**

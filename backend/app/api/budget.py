"""
Budget API Routes
Handles transaction uploads, categorization, and spending analysis
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import io
import logging

from app.agents.budget_agent import BudgetAgent

logger = logging.getLogger(__name__)

router = APIRouter()


class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    category: Optional[str] = None
    account: Optional[str] = None


class AnalysisRequest(BaseModel):
    transactions: List[Transaction]
    monthly_income: Optional[float] = None


class AnalysisResponse(BaseModel):
    total_spent: float
    total_income: float
    by_category: dict
    top_categories: List[dict]
    insights: List[str]
    budget_recommendations: Optional[dict] = None


@router.post("/upload-csv")
async def upload_transactions(
    file: UploadFile = File(...),
    request: Request = None
):
    """
    Upload CSV file with transactions
    Expected columns: date, description, amount, [category]
    """
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = ["date", "description", "amount"]
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain columns: {required_columns}"
            )
        
        # Convert to transactions
        transactions = []
        for _, row in df.iterrows():
            txn = {
                "date": str(row["date"]),
                "description": str(row["description"]),
                "amount": float(row["amount"]),
                "category": str(row.get("category", "")) if "category" in df.columns else None,
                "account": str(row.get("account", "")) if "account" in df.columns else None
            }
            transactions.append(txn)
        
        # Initialize agent
        llm_service = request.app.state.llm_service
        vector_service = request.app.state.vector_service
        agent = BudgetAgent(llm_service, vector_service)
        
        # Categorize transactions
        categorized = agent.categorize_transactions_batch(transactions)
        
        logger.info(f"Uploaded and categorized {len(categorized)} transactions")
        
        return {
            "status": "success",
            "transaction_count": len(categorized),
            "transactions": categorized
        }
        
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_spending(
    data: AnalysisRequest,
    request: Request
):
    """
    Analyze spending patterns and generate insights
    """
    try:
        # Initialize agent
        llm_service = request.app.state.llm_service
        vector_service = request.app.state.vector_service
        agent = BudgetAgent(llm_service, vector_service)
        
        # Convert to dict format
        transactions = [txn.model_dump() for txn in data.transactions]
        
        # Categorize if not already categorized
        categorized = agent.categorize_transactions_batch(transactions)
        
        # Analyze spending
        analysis = agent.analyze_spending(categorized)
        
        # Generate insights
        insights = await agent.generate_insights(
            analysis,
            user_income=data.monthly_income
        )
        
        # Generate budget recommendations if income provided
        budget_recs = None
        if data.monthly_income:
            budget_recs = await agent.get_budget_recommendations(
                analysis,
                data.monthly_income
            )
        
        return AnalysisResponse(
            total_spent=analysis["total_spent"],
            total_income=analysis["total_income"],
            by_category=analysis["by_category"],
            top_categories=analysis["top_categories"],
            insights=insights,
            budget_recommendations=budget_recs
        )
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/categorize")
async def categorize_transaction(
    transaction: Transaction,
    request: Request
):
    """
    Categorize a single transaction
    """
    try:
        llm_service = request.app.state.llm_service
        vector_service = request.app.state.vector_service
        agent = BudgetAgent(llm_service, vector_service)
        
        category = agent.categorize_transaction(
            transaction.description,
            transaction.amount
        )
        
        return {
            "transaction": transaction.model_dump(),
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Categorization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

"""
Budget Analysis Agent
Categorizes transactions, analyzes spending patterns, generates insights
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class BudgetAgent:
    """
    Budget Analysis Agent
    - Categorizes transactions
    - Analyzes spending patterns
    - Generates personalized insights
    """
    
    # Common transaction categories
    CATEGORIES = {
        "Housing": ["rent", "mortgage", "property tax", "hoa", "home insurance"],
        "Transportation": ["gas", "fuel", "uber", "lyft", "car payment", "auto insurance", "parking"],
        "Food & Dining": ["grocery", "restaurant", "cafe", "starbucks", "food", "dining"],
        "Utilities": ["electric", "water", "internet", "phone", "gas bill"],
        "Healthcare": ["doctor", "hospital", "pharmacy", "medical", "health insurance"],
        "Entertainment": ["netflix", "spotify", "movie", "concert", "game"],
        "Shopping": ["amazon", "target", "walmart", "clothing", "electronics"],
        "Personal Care": ["gym", "salon", "haircut", "spa"],
        "Education": ["tuition", "books", "course"],
        "Subscriptions": ["subscription", "membership"],
        "Insurance": ["insurance"],
        "Debt Payment": ["loan", "credit card payment"],
        "Savings": ["savings", "investment"],
        "Income": ["salary", "paycheck", "income", "deposit"],
        "Other": []
    }
    
    def __init__(self, llm_service: LLMService, vector_service: VectorService):
        self.llm = llm_service
        self.vector = vector_service
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a single transaction using rule-based + LLM fallback
        
        Args:
            description: Transaction description
            amount: Transaction amount
        
        Returns:
            Category name
        """
        description_lower = description.lower()
        
        # Rule-based categorization (fast, free)
        for category, keywords in self.CATEGORIES.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # If amount is positive and large, likely income
        if amount > 0 and amount > 100:
            return "Income"
        
        # Default fallback
        return "Other"
    
    def categorize_transactions_batch(
        self,
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Categorize multiple transactions
        
        Args:
            transactions: List of transaction dicts
        
        Returns:
            Transactions with added category field
        """
        categorized = []
        
        for txn in transactions:
            category = self.categorize_transaction(
                txn.get("description", ""),
                txn.get("amount", 0)
            )
            
            txn_copy = txn.copy()
            txn_copy["category"] = category
            categorized.append(txn_copy)
        
        return categorized
    
    def analyze_spending(
        self,
        transactions: List[Dict[str, Any]],
        period: str = "month"
    ) -> Dict[str, Any]:
        """
        Analyze spending patterns
        
        Args:
            transactions: List of categorized transactions
            period: Analysis period (month, week, year)
        
        Returns:
            Analysis results with spending by category, trends, etc.
        """
        if not transactions:
            return {
                "total_spent": 0,
                "by_category": {},
                "insights": []
            }
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(transactions)
        
        # Filter expenses (negative amounts)
        expenses_df = df[df["amount"] < 0].copy()
        expenses_df["amount"] = expenses_df["amount"].abs()
        
        # Calculate totals by category
        by_category = expenses_df.groupby("category")["amount"].sum().to_dict()
        
        # Total spent
        total_spent = expenses_df["amount"].sum()
        
        # Find top spending categories
        top_categories = sorted(
            by_category.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Calculate income
        income_df = df[df["amount"] > 0]
        total_income = income_df["amount"].sum()
        
        return {
            "total_spent": round(total_spent, 2),
            "total_income": round(total_income, 2),
            "by_category": {k: round(v, 2) for k, v in by_category.items()},
            "top_categories": [
                {"category": cat, "amount": round(amt, 2)}
                for cat, amt in top_categories
            ],
            "transaction_count": len(transactions),
            "average_transaction": round(total_spent / len(expenses_df), 2) if len(expenses_df) > 0 else 0
        }
    
    async def generate_insights(
        self,
        analysis: Dict[str, Any],
        user_income: Optional[float] = None
    ) -> List[str]:
        """
        Generate personalized insights using LLM
        
        Args:
            analysis: Spending analysis results
            user_income: User's monthly income (optional)
        
        Returns:
            List of insight strings
        """
        try:
            # Get relevant budgeting tips from vector DB
            top_category = analysis["top_categories"][0]["category"] if analysis["top_categories"] else "general"
            tips = self.vector.search(
                query=f"budgeting tips for {top_category}",
                collection_name="budgeting_tips",
                n_results=2
            )
            
            # Build context for LLM
            context = f"""
            Spending Analysis:
            - Total spent: ${analysis['total_spent']}
            - Total income: ${analysis.get('total_income', 'N/A')}
            - Top spending category: {top_category} (${analysis['top_categories'][0]['amount']})
            
            Relevant Tips:
            {chr(10).join([f"- {tip['text']}" for tip in tips])}
            """
            
            system_prompt = """You are a friendly financial advisor. Generate 3-4 specific, actionable insights
            about the user's spending. Be encouraging but honest. Focus on:
            1. One notable observation about their spending
            2. One area for improvement with a specific suggestion
            3. One positive aspect of their financial behavior
            
            Keep each insight to 1-2 sentences. Be conversational and supportive."""
            
            prompt = f"{context}\n\nGenerate insights about this spending pattern."
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            # Parse insights (expecting numbered or bulleted list)
            insights = [
                line.strip().lstrip("123456789.-•* ")
                for line in response.split("\n")
                if line.strip() and len(line.strip()) > 20
            ]
            
            return insights[:4]  # Max 4 insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            # Return fallback insights
            return [
                f"Your top spending category is {top_category}, totaling ${analysis['top_categories'][0]['amount']}.",
                "Consider reviewing this category for potential savings opportunities."
            ]
    
    async def get_budget_recommendations(
        self,
        analysis: Dict[str, Any],
        monthly_income: float
    ) -> Dict[str, float]:
        """
        Generate budget recommendations based on 50/30/20 rule
        
        Args:
            analysis: Spending analysis
            monthly_income: User's monthly income
        
        Returns:
            Recommended budget allocations by category
        """
        return {
            "Needs (50%)": round(monthly_income * 0.5, 2),
            "Wants (30%)": round(monthly_income * 0.3, 2),
            "Savings (20%)": round(monthly_income * 0.2, 2)
        }

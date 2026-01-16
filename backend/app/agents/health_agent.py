"""
Financial Health Score Agent
Calculates overall financial wellness score
Provides breakdown and actionable recommendations
"""
import logging
from typing import Dict, Any, List, Optional
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)


class HealthScoreAgent:
    """
    Financial Health Score Agent
    - Calculates 0-100 health score
    - Provides detailed breakdown
    - Generates improvement recommendations
    """
    
    def __init__(self, llm_service: LLMService, vector_service: VectorService):
        self.llm = llm_service
        self.vector = vector_service
    
    def calculate_health_score(
        self,
        monthly_income: float,
        monthly_expenses: float,
        total_savings: float,
        total_debt: float = 0,
        emergency_fund: float = 0,
    ) -> Dict[str, Any]:
        """
        Calculate financial health score (0-100)
        
        Components:
        1. Emergency Fund (30%): 3-6 months expenses saved
        2. Debt-to-Income Ratio (25%): <36% is healthy
        3. Savings Rate (25%): >20% is excellent
        4. Budget Adherence (20%): Spending vs income
        
        Args:
            monthly_income: Monthly income
            monthly_expenses: Average monthly expenses
            total_savings: Total savings balance
            total_debt: Total debt amount
            emergency_fund: Emergency fund balance
        
        Returns:
            Health score with breakdown
        """
        scores = {}
        weights = {
            "emergency_fund": 0.30,
            "debt_management": 0.25,
            "savings_rate": 0.25,
            "budget_adherence": 0.20
        }
        
        # 1. Emergency Fund Score
        if monthly_expenses > 0:
            months_covered = emergency_fund / monthly_expenses
            if months_covered >= 6:
                emergency_score = 100
            elif months_covered >= 3:
                emergency_score = 70 + (months_covered - 3) * 10
            else:
                emergency_score = (months_covered / 3) * 70
        else:
            emergency_score = 50
        
        scores["emergency_fund"] = {
            "score": round(emergency_score, 1),
            "weight": weights["emergency_fund"],
            "months_covered": round(months_covered, 1) if monthly_expenses > 0 else 0,
            "target": "3-6 months of expenses",
            "status": self._get_status(emergency_score)
        }
        
        # 2. Debt-to-Income Ratio Score
        if monthly_income > 0:
            # Assume monthly debt payment is 5% of total debt (simplified)
            monthly_debt_payment = total_debt * 0.05 / 12
            debt_to_income = (monthly_debt_payment / monthly_income) * 100
            
            if debt_to_income <= 15:
                debt_score = 100
            elif debt_to_income <= 28:
                debt_score = 90 - (debt_to_income - 15) * 2
            elif debt_to_income <= 36:
                debt_score = 70 - (debt_to_income - 28) * 3
            else:
                debt_score = max(0, 50 - (debt_to_income - 36) * 2)
        else:
            debt_score = 50
            debt_to_income = 0
        
        scores["debt_management"] = {
            "score": round(debt_score, 1),
            "weight": weights["debt_management"],
            "debt_to_income_ratio": round(debt_to_income, 1),
            "target": "<36% (excellent <15%)",
            "status": self._get_status(debt_score)
        }
        
        # 3. Savings Rate Score
        if monthly_income > 0:
            monthly_savings = monthly_income - monthly_expenses
            savings_rate = (monthly_savings / monthly_income) * 100
            
            if savings_rate >= 20:
                savings_score = 100
            elif savings_rate >= 10:
                savings_score = 70 + (savings_rate - 10) * 3
            elif savings_rate >= 0:
                savings_score = savings_rate * 7
            else:
                savings_score = 0  # Spending more than earning
        else:
            savings_score = 50
            savings_rate = 0
        
        scores["savings_rate"] = {
            "score": round(savings_score, 1),
            "weight": weights["savings_rate"],
            "current_rate": round(savings_rate, 1),
            "target": "20%+ of income",
            "status": self._get_status(savings_score)
        }
        
        # 4. Budget Adherence Score
        if monthly_income > 0:
            expense_ratio = (monthly_expenses / monthly_income) * 100
            
            if expense_ratio <= 70:
                budget_score = 100
            elif expense_ratio <= 80:
                budget_score = 90 - (expense_ratio - 70) * 2
            elif expense_ratio <= 90:
                budget_score = 70 - (expense_ratio - 80) * 3
            else:
                budget_score = max(0, 50 - (expense_ratio - 90) * 5)
        else:
            budget_score = 50
            expense_ratio = 0
        
        scores["budget_adherence"] = {
            "score": round(budget_score, 1),
            "weight": weights["budget_adherence"],
            "expense_ratio": round(expense_ratio, 1),
            "target": "<80% of income",
            "status": self._get_status(budget_score)
        }
        
        # Calculate overall score
        overall_score = sum(
            scores[component]["score"] * scores[component]["weight"]
            for component in scores
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": self._get_grade(overall_score),
            "components": scores,
            "summary": self._get_summary(overall_score)
        }
    
    def _get_status(self, score: float) -> str:
        """Get status emoji based on score"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "needs_improvement"
    
    def _get_grade(self, score: float) -> str:
        """Get letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_summary(self, score: float) -> str:
        """Get summary message"""
        if score >= 80:
            return "Excellent financial health! Keep up the great work."
        elif score >= 60:
            return "Good financial health with room for improvement."
        elif score >= 40:
            return "Fair financial health. Focus on key areas for improvement."
        else:
            return "Financial health needs attention. Let's create an improvement plan."
    
    async def generate_action_items(
        self,
        health_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate top 3 action items to improve financial health
        
        Args:
            health_data: Health score calculation results
        
        Returns:
            List of prioritized action items
        """
        # Find weakest components
        components = health_data["components"]
        sorted_components = sorted(
            components.items(),
            key=lambda x: x[1]["score"]
        )
        
        # Focus on bottom 2-3 components
        weak_areas = sorted_components[:3]
        
        action_items = []
        
        for area_name, area_data in weak_areas:
            if area_data["score"] < 70:  # Only if needs improvement
                # Get relevant tips from vector DB
                tips = self.vector.search(
                    query=f"improve {area_name.replace('_', ' ')}",
                    collection_name="financial_knowledge",
                    n_results=1
                )
                
                action = {
                    "area": area_name.replace("_", " ").title(),
                    "current_score": area_data["score"],
                    "target": area_data["target"],
                    "priority": "high" if area_data["score"] < 40 else "medium"
                }
                
                # Generate specific action using LLM
                try:
                    system_prompt = """Generate ONE specific, actionable recommendation (1-2 sentences).
                    Be direct and practical."""
                    
                    prompt = f"""
                    Financial area: {area_name}
                    Current status: {area_data}
                    Relevant tip: {tips[0]['text'] if tips else 'N/A'}
                    
                    What's ONE specific action to improve this?
                    """
                    
                    recommendation = await self.llm.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=0.7,
                        max_tokens=100
                    )
                    
                    action["recommendation"] = recommendation.strip()
                except Exception as e:
                    logger.error(f"Failed to generate action: {e}")
                    action["recommendation"] = f"Focus on improving {area_name.replace('_', ' ')} to reach target: {area_data['target']}"
                
                action_items.append(action)
        
        return action_items[:3]  # Return top 3
    
    def compare_to_peers(
        self,
        score: float,
        age: Optional[int] = None,
        income_bracket: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare user's score to peer averages (simplified)
        
        Args:
            score: User's health score
            age: User's age
            income_bracket: Income bracket (low, medium, high)
        
        Returns:
            Comparison data
        """
        # Simplified peer averages (in production, use real data)
        peer_averages = {
            "18-25": 55,
            "26-35": 62,
            "36-45": 68,
            "46-55": 72,
            "56+": 75
        }
        
        if age:
            if age < 26:
                peer_avg = peer_averages["18-25"]
            elif age < 36:
                peer_avg = peer_averages["26-35"]
            elif age < 46:
                peer_avg = peer_averages["36-45"]
            elif age < 56:
                peer_avg = peer_averages["46-55"]
            else:
                peer_avg = peer_averages["56+"]
        else:
            peer_avg = 65  # Overall average
        
        difference = score - peer_avg
        
        if difference > 10:
            message = "You're doing significantly better than your peers!"
        elif difference > 0:
            message = "You're ahead of your peers. Keep it up!"
        elif difference > -10:
            message = "You're close to the average. Small improvements will make a big difference."
        else:
            message = "There's opportunity to catch up to peers. Focus on key areas."
        
        return {
            "your_score": score,
            "peer_average": peer_avg,
            "difference": round(difference, 1),
            "percentile": min(99, max(1, 50 + (difference * 2))),
            "message": message
        }

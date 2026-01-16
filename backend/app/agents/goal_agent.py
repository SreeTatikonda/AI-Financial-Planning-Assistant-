"""
Goal Planning Agent
Helps users set and track financial goals
Provides savings recommendations and progress tracking
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class GoalPlanningAgent:
    """
    Goal Planning Agent
    - Creates savings plans
    - Tracks goal progress
    - Generates recommendations
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    def calculate_savings_plan(
        self,
        target_amount: float,
        current_amount: float,
        deadline: datetime,
        monthly_income: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate how much to save monthly to reach goal
        
        Args:
            target_amount: Goal target
            current_amount: Current progress
            deadline: Goal deadline
            monthly_income: User's income (for feasibility check)
        
        Returns:
            Savings plan with monthly amount, feasibility, milestones
        """
        # Calculate remaining amount and time
        remaining_amount = target_amount - current_amount
        
        if deadline:
            months_remaining = max(1, (deadline - datetime.now()).days / 30)
        else:
            months_remaining = 12  # Default to 1 year
        
        # Monthly savings needed
        monthly_needed = remaining_amount / months_remaining
        
        # Check feasibility
        feasible = True
        feasibility_message = "Goal is achievable with consistent saving."
        
        if monthly_income:
            percentage_of_income = (monthly_needed / monthly_income) * 100
            
            if percentage_of_income > 50:
                feasible = False
                feasibility_message = f"This goal requires {percentage_of_income:.1f}% of your income, which may not be sustainable."
            elif percentage_of_income > 30:
                feasibility_message = f"This goal requires {percentage_of_income:.1f}% of your income. Consider extending the deadline."
        
        # Generate milestones (quarterly checkpoints)
        milestones = []
        for i in range(1, int(months_remaining) + 1, 3):
            milestone_date = datetime.now() + timedelta(days=i * 30)
            milestone_amount = current_amount + (monthly_needed * i)
            
            if milestone_date <= deadline:
                milestones.append({
                    "date": milestone_date.strftime("%Y-%m-%d"),
                    "target_amount": round(milestone_amount, 2),
                    "months_from_now": i
                })
        
        return {
            "remaining_amount": round(remaining_amount, 2),
            "months_remaining": round(months_remaining, 1),
            "monthly_savings_needed": round(monthly_needed, 2),
            "feasible": feasible,
            "feasibility_message": feasibility_message,
            "percentage_of_income": round(percentage_of_income, 1) if monthly_income else None,
            "milestones": milestones
        }
    
    def calculate_progress(
        self,
        current_amount: float,
        target_amount: float
    ) -> Dict[str, Any]:
        """
        Calculate goal progress
        
        Args:
            current_amount: Current savings
            target_amount: Target amount
        
        Returns:
            Progress metrics
        """
        percentage = (current_amount / target_amount) * 100 if target_amount > 0 else 0
        remaining = target_amount - current_amount
        
        # Status
        if percentage >= 100:
            status = "completed"
            message = "🎉 Goal achieved!"
        elif percentage >= 75:
            status = "on_track"
            message = "Great progress! You're almost there."
        elif percentage >= 50:
            status = "on_track"
            message = "You're halfway to your goal!"
        elif percentage >= 25:
            status = "needs_attention"
            message = "Keep going, you're making progress."
        else:
            status = "needs_attention"
            message = "Consider increasing your monthly savings to stay on track."
        
        return {
            "percentage": round(percentage, 1),
            "remaining": round(remaining, 2),
            "status": status,
            "message": message
        }
    
    async def generate_recommendations(
        self,
        goal_name: str,
        savings_plan: Dict[str, Any],
        current_spending: Optional[Dict[str, float]] = None
    ) -> List[str]:
        """
        Generate personalized recommendations to reach goal
        
        Args:
            goal_name: Name of the goal
            savings_plan: Calculated savings plan
            current_spending: User's spending by category
        
        Returns:
            List of recommendations
        """
        try:
            context = f"""
            Goal: {goal_name}
            Monthly savings needed: ${savings_plan['monthly_savings_needed']}
            Months remaining: {savings_plan['months_remaining']}
            Feasible: {savings_plan['feasible']}
            """
            
            if current_spending:
                context += f"\nCurrent spending breakdown:\n"
                for category, amount in current_spending.items():
                    context += f"- {category}: ${amount}\n"
            
            system_prompt = """You are a supportive financial coach. Generate 3 specific, actionable 
            recommendations to help the user reach their goal. Be encouraging and practical.
            Focus on:
            1. How to find the required monthly savings
            2. Specific spending areas to reduce (if spending data available)
            3. Motivation or alternative strategies
            
            Keep each recommendation to 1-2 sentences."""
            
            prompt = f"{context}\n\nGenerate recommendations to help reach this goal."
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=300
            )
            
            # Parse recommendations
            recommendations = [
                line.strip().lstrip("123456789.-•* ")
                for line in response.split("\n")
                if line.strip() and len(line.strip()) > 20
            ]
            
            return recommendations[:3]
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            # Fallback recommendations
            return [
                f"Save ${savings_plan['monthly_savings_needed']} per month to reach your goal on time.",
                "Set up automatic transfers to your savings account on payday.",
                "Review your budget monthly and adjust as needed."
            ]
    
    def prioritize_goals(
        self,
        goals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize multiple goals based on urgency and importance
        
        Args:
            goals: List of goal dictionaries
        
        Returns:
            Sorted list of goals with priority scores
        """
        scored_goals = []
        
        for goal in goals:
            score = 0
            
            # Urgency: closer deadline = higher priority
            if goal.get("deadline"):
                days_until = (goal["deadline"] - datetime.now()).days
                if days_until < 90:
                    score += 3
                elif days_until < 180:
                    score += 2
                else:
                    score += 1
            
            # Importance: user-defined priority
            priority = goal.get("priority", 2)
            if priority == 1:  # High
                score += 3
            elif priority == 2:  # Medium
                score += 2
            else:  # Low
                score += 1
            
            # Progress: goals closer to completion
            percentage = (goal.get("current_amount", 0) / goal.get("target_amount", 1)) * 100
            if percentage > 75:
                score += 2
            elif percentage > 50:
                score += 1
            
            goal_copy = goal.copy()
            goal_copy["priority_score"] = score
            scored_goals.append(goal_copy)
        
        # Sort by priority score (descending)
        return sorted(scored_goals, key=lambda x: x["priority_score"], reverse=True)

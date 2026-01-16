"""
Goals API Routes
Handles goal creation, tracking, and progress updates
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import logging

from app.agents.goal_agent import GoalPlanningAgent

logger = logging.getLogger(__name__)

router = APIRouter()


class GoalCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float = 0.0
    deadline: Optional[str] = None
    priority: int = 2  # 1=high, 2=medium, 3=low
    monthly_income: Optional[float] = None


class GoalUpdate(BaseModel):
    amount: float
    note: Optional[str] = None


class GoalResponse(BaseModel):
    id: str
    name: str
    target_amount: float
    current_amount: float
    deadline: Optional[str]
    progress: dict
    savings_plan: dict
    recommendations: List[str]


@router.post("/create", response_model=GoalResponse)
async def create_goal(
    goal: GoalCreate,
    request: Request
):
    """
    Create a new financial goal
    """
    try:
        llm_service = request.app.state.llm_service
        agent = GoalPlanningAgent(llm_service)
        
        # Parse deadline
        deadline = None
        if goal.deadline:
            deadline = datetime.fromisoformat(goal.deadline)
        
        # Calculate savings plan
        savings_plan = agent.calculate_savings_plan(
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            deadline=deadline,
            monthly_income=goal.monthly_income
        )
        
        # Calculate progress
        progress = agent.calculate_progress(
            current_amount=goal.current_amount,
            target_amount=goal.target_amount
        )
        
        # Generate recommendations
        recommendations = await agent.generate_recommendations(
            goal_name=goal.name,
            savings_plan=savings_plan
        )
        
        # Generate goal ID (in production, save to database)
        goal_id = f"goal_{int(datetime.now().timestamp())}"
        
        logger.info(f"Created goal: {goal.name} (ID: {goal_id})")
        
        return GoalResponse(
            id=goal_id,
            name=goal.name,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            deadline=goal.deadline,
            progress=progress,
            savings_plan=savings_plan,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Goal creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{goal_id}/update")
async def update_goal_progress(
    goal_id: str,
    update: GoalUpdate,
    request: Request
):
    """
    Update progress on a goal
    """
    try:
        # In production, fetch goal from database
        # For now, return mock response
        
        logger.info(f"Updated goal {goal_id}: +${update.amount}")
        
        return {
            "status": "success",
            "goal_id": goal_id,
            "amount_added": update.amount,
            "note": update.note,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Goal update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{goal_id}")
async def get_goal(
    goal_id: str,
    request: Request
):
    """
    Get goal details and current progress
    """
    try:
        # In production, fetch from database
        # Mock response for now
        
        return {
            "id": goal_id,
            "name": "Emergency Fund",
            "target_amount": 10000,
            "current_amount": 5000,
            "progress": 50,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Failed to get goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prioritize")
async def prioritize_goals(
    goals: List[GoalCreate],
    request: Request
):
    """
    Prioritize multiple goals
    """
    try:
        llm_service = request.app.state.llm_service
        agent = GoalPlanningAgent(llm_service)
        
        # Convert to dict format
        goals_data = []
        for g in goals:
            goal_dict = g.model_dump()
            if g.deadline:
                goal_dict["deadline"] = datetime.fromisoformat(g.deadline)
            goals_data.append(goal_dict)
        
        # Prioritize
        prioritized = agent.prioritize_goals(goals_data)
        
        return {
            "prioritized_goals": prioritized
        }
        
    except Exception as e:
        logger.error(f"Goal prioritization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

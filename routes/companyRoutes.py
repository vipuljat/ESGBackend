from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Union
from services.companyService import create_plant
from services.plantService import bulk_update_plant_esg_data


company_router = APIRouter(prefix="/company", tags=["Company"])


@company_router.post("/{company_id}/plants")
async def create_company_plant(
    company_id: str,
    plant_data: Dict[str, Any],
    user_role: str = Query(..., description="User role (e.g., company_admin)"),
):
    """
    Create a new plant for a specific company.
    """
    try:
        result = await create_plant(company_id, plant_data, user_role)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
from fastapi import APIRouter, HTTPException
from typing import Dict, Union
from services.plantService import bulk_update_plant_esg_data, update_plant_esg_data

router = APIRouter(prefix="/plants", tags=["Plants"])

@router.post("/{plant_id}/updateEsgSingle")
async def update_plant_esg_single(plant_id: str, esg_data: Dict[str, Union[Dict, str]], user_role: str = "plant_manager"):
    try:
        if len(esg_data) != 1:
            raise HTTPException(status_code=400, detail="Expected exactly one question name and response")
        question_name, response = next(iter(esg_data.items()))
        # Wrap string response in a dict for consistency
        if isinstance(response, str):
            response = {"value": response}
        result = await update_plant_esg_data(plant_id, question_name, response, user_role)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


#Bulk update ESG data
@router.post("/{plant_id}/updateEsg")
async def update_plant_esg(plant_id: str, esg_data: Dict[str, Union[Dict, str, list]], user_role: str = "plant_manager"):
    try:
        if not esg_data:
            raise HTTPException(status_code=400, detail="No data provided for update")
        # Process each response, wrapping strings in a dict for consistency
        processed_data = {}
        for question_name, response in esg_data.items():
            if isinstance(response, str):
                processed_data[question_name] = {"value": response}
            else:
                processed_data[question_name] = response
        result = await bulk_update_plant_esg_data(plant_id, processed_data, user_role)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
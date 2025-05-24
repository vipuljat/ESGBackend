from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from typing import Any, Dict
from database import db
from mappings import QUESTION_MAPPINGS, STRING_RESPONSE_QUESTIONS
from models import Company, Plant, UpdateLog

plants_collection = db["plants"]
company_collection = db["company"]
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from typing import Any, Dict
from database import db
from models import Company, Plant, UpdateLog

plants_collection = db["plants"]
company_collection = db["company"]

async def create_plant(company_id: str, plant_data: Dict[str, Any], user_role: str) -> Dict[str, str]:
    """
    Create a new plant with required fields provided by the user, keeping sectional details empty.

    Args:
        company_id (str): The ID of the company (e.g., COMP001).
        plant_data (Dict[str, Any]): Dictionary with plant_id, plant_name, plant_manager, location,
                                    operational_status, establishment_date, production_capacity, reporting_year.
        user_role (str): The role of the user (e.g., company_admin).

    Returns:
        Dict[str, str]: A message confirming the plant creation.

    Raises:
        HTTPException: If validation fails, company not found, or unauthorized.
    """
    # Check if company exists
    company = company_collection.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    # Validate company as Pydantic model
    try:
        company_model = Company(**company)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid company data: {str(e)}")

    # Check user role authorization
    allowed_roles = company_model.data_ownership.get("plants", ["company_admin"])
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"User role {user_role} not authorized to create plants for {company_id}"
        )

    # Validate required fields
    required_fields = [
        "plant_id", "plant_name", "plant_manager", "location",
        "operational_status", "establishment_date", "production_capacity", "reporting_year"
    ]
    missing_fields = [field for field in required_fields if field not in plant_data or plant_data[field] is None]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")

    # Check if plant_id is unique
    if plants_collection.find_one({"plant_id": plant_data["plant_id"]}):
        raise HTTPException(status_code=400, detail=f"Plant {plant_data['plant_id']} already exists")

    # Set company_id directly as string
    plant_data["company_id"] = company_id


    # Set default fields
    plant_data.setdefault("general_disclosures", {})
    plant_data.setdefault("management_and_process", {})
    plant_data.setdefault("principle_wise_performance", {})
    plant_data.setdefault("data_ownership", {})
    plant_data.setdefault("updates", [])
    plant_data.setdefault("created_at", datetime.utcnow())
    plant_data.setdefault("updated_at", datetime.utcnow())

    # Add creation log
    creation_log = UpdateLog(
        question_id="CREATE",
        updated_by=user_role,
        updated_at=datetime.utcnow(),
        schema_path="plant"
    )
    plant_data["updates"] = [creation_log.dict()]

    # Validate plant data
    try:
        plant_model = Plant(**plant_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid plant data: {str(e)}")

    # Insert plant
    try:
        result = plants_collection.insert_one(plant_model.dict(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plant: {str(e)}")

    # Update company's plants array
    try:
        company_collection.update_one(
            {"company_id": company_id},
            {"$push": {"plants": plant_data["plant_id"]}}
        )
    except Exception as e:
        # Roll back plant creation
        plants_collection.delete_one({"plant_id": plant_data["plant_id"]})
        raise HTTPException(status_code=500, detail=f"Failed to update company: {str(e)}")

    return {"message": f"Plant {plant_data['plant_id']} created successfully for company {company_id}"}
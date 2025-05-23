from fastapi import HTTPException
from datetime import datetime
from typing import Dict
from database import db
from mappings import QUESTION_MAPPINGS

# Access plants collection
plants_collection = db["plants"]

async def update_plant_esg_data(plant_id: str, question_name: str, response: Dict, user_role: str) -> dict:
    """Update ESG data for a plant in the plants collection."""
    # Find plant
    plant = plants_collection.find_one({"plant_id": plant_id})
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # Get mapping for question name
    mapping = QUESTION_MAPPINGS.get(question_name)
    if not mapping:
        raise HTTPException(status_code=400, detail=f"Invalid question name: {question_name}")
    
    question_id = mapping["question_id"]
    schema_path = mapping["schema_path"]

    # Construct data_ownership key
    path_parts = schema_path.split(".")
    if path_parts[0] == "general_disclosures":
        ownership_key = "general_disclosures"
    elif path_parts[0] == "principle_wise_performance" and len(path_parts) > 1:
        ownership_key = f"principle_wise_performance.{path_parts[1]}"
    else:
        ownership_key = path_parts[0]

    # Validate role
    allowed_roles = plant.get("data_ownership", {}).get(ownership_key, [])
    if user_role not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"Unauthorized role: {user_role} not in {allowed_roles}")

    # Extract string value for specific questions
    final_response = response.get("value", response) if question_name in ["Facility Type", "Location", "Operational Since"] else response

    # Update plant document
    update_result = plants_collection.update_one(
        {"plant_id": plant_id},
        {
            "$set": {
                schema_path: final_response,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "updates": {
                    "question_id": question_id,
                    "updated_by": user_role,
                    "updated_at": datetime.utcnow(),
                    "schema_path": schema_path
                }
            }
        },
        upsert=True
    )

    if update_result.modified_count > 0 or update_result.upserted_id:
        return {"message": f"Updated {question_id} for plant {plant_id}"}
    raise HTTPException(status_code=500, detail="Update failed")
from fastapi import HTTPException
from datetime import datetime
from typing import Any, Dict
from database import db
from mappings import QUESTION_MAPPINGS, STRING_RESPONSE_QUESTIONS
from models import Plant, UpdateLog

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



async def bulk_update_plant_esg_data(
    plant_id: str,
    esg_data: Dict[str, Any],
    user_role: str
) -> Dict[str, str]:
    """
    Bulk update ESG data for a plant based on question names and responses.
    """
    # 1. Make sure the plant exists
    plant = plants_collection.find_one({"plant_id": plant_id})
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")

    # 2. Validate current plant data
    try:
        plant_model = Plant(**plant)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid plant data: {str(e)}")

    updates = []
    update_messages = []

    # 3. Loop through every question the client sent
    for question_name, response in esg_data.items():

        # 3-a. Check the question exists in our mapping
        if question_name not in QUESTION_MAPPINGS:
            raise HTTPException(status_code=400, detail=f"Invalid question name: {question_name}")

        mapping = QUESTION_MAPPINGS[question_name]
        question_id = mapping["question_id"]
        schema_path = mapping["schema_path"]

        # 3-b. Check ownership / permissions
        if plant_model.data_ownership and schema_path in plant_model.data_ownership:
            allowed_roles = plant_model.data_ownership[schema_path]
        else:
            allowed_roles = ["plant_manager", "company_admin"]

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"User role {user_role} not authorized to update {schema_path}"
            )

        # 3-c. Build the MongoDB update doc
        # ---- LOCATION (special case, partial update) ----
        if schema_path == "location" and isinstance(response, dict):
            update_field = {"$set": {
                f"{schema_path}.{k}": v for k, v in response.items()
                if k in ["street", "city", "state", "country", "pincode", "coordinates"]
            }}
            if not update_field["$set"]:
                raise HTTPException(status_code=400, detail="No valid location fields provided")

        # ---- SIMPLE STRING QUESTIONS ----
        elif question_name in STRING_RESPONSE_QUESTIONS:
            # Client must send {"value": "some string"}
            if not isinstance(response, dict) or "value" not in response:
                raise HTTPException(
                    status_code=400,
                    detail=f"String response for {question_name} must be wrapped in {{'value': str}}"
                )
            response_value = response["value"]
            update_field = {"$set": {schema_path: response_value}}

        # ---- EVERYTHING ELSE (lists, dicts, etc.) ----
        else:
            update_field = {"$set": {schema_path: response}}

        # 3-d. Validate the *prospective* plant state with this change
        try:
            temp_plant = plant.copy()
            # Walk the dotted path and set the value in a temp dict
            cur = temp_plant
            parts = schema_path.split(".")
            for part in parts[:-1]:
                if part not in cur or cur[part] is None:
                    cur[part] = {}
                cur = cur[part]
            cur[parts[-1]] = (
                response_value if question_name in STRING_RESPONSE_QUESTIONS else response
            )
            Plant(**temp_plant)   # will raise if wrong
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid response for {question_name}: {str(e)}")

        # 3-e. Add to batch update & logs
        log_entry = UpdateLog(
            question_id=question_id,
            updated_by=user_role,
            updated_at=datetime.utcnow(),
            schema_path=schema_path
        ).dict()

        updates.append(update_field)
        update_messages.append(f"Updated {question_id} for plant {plant_id}")
        updates.append({"$push": {"updates": log_entry}})

    # 4. Combine all $set operations + push logs atomically
    combined_update = {"$set": {}, "$push": {"updates": {"$each": []}}}
    for op in updates:
        if "$set" in op:
            combined_update["$set"].update(op["$set"])
        if "$push" in op:
            combined_update["$push"]["updates"]["$each"].append(op["$push"]["updates"])

    combined_update["$set"]["updated_at"] = datetime.utcnow()

    # 5. Execute update
    try:
        result = plants_collection.update_one({"plant_id": plant_id}, combined_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update plant data")

    return {"message": "; ".join(update_messages)}
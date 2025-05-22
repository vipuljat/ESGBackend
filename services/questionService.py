from typing import List
from fastapi import HTTPException
from models import ESGQuestion, ESGQuestionUpdate
from database import get_collection
from utils.helpers import parse_question_id

def create_or_update_question(question: ESGQuestion) -> ESGQuestion:
    collection = get_collection()
    
    # Check if question exists, if yes update, else create
    existing = collection.find_one({"question_id": question.question_id})
    if existing:
        collection.update_one(
            {"question_id": question.question_id},
            {"$set": {"response": question.response}}
        )
    else:
        collection.insert_one(question.dict())
    
    return question

def bulk_upload_questions(questions: List[ESGQuestion]) -> List[ESGQuestion]:
    collection = get_collection()
    
    for question in questions:
        existing = collection.find_one({"question_id": question.question_id})
        if existing:
            collection.update_one(
                {"question_id": question.question_id},
                {"$set": {"response": question.response}}
            )
        else:
            collection.insert_one(question.dict())
    
    return questions

def get_question(question_id: str) -> ESGQuestion:
    collection = get_collection()
    
    question = collection.find_one({"question_id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return ESGQuestion.parse_obj(question)

def update_question_response(question_id: str, update: ESGQuestionUpdate) -> ESGQuestion:
    collection = get_collection()
    
    question = collection.find_one({"question_id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    collection.update_one(
        {"question_id": question_id},
        {"$set": {"response": update.response}}
    )
    
    updated_question = collection.find_one({"question_id": question_id})
    if not updated_question:  # This should never happen since we just updated it, but for type safety
        raise HTTPException(status_code=500, detail="Failed to retrieve updated question")
    
    return ESGQuestion.parse_obj(updated_question)

def get_questions_by_section(section: str) -> List[ESGQuestion]:
    if section not in ["A", "B", "C"]:
        raise HTTPException(status_code=400, detail="Invalid section")
    
    collection = get_collection()
    
    # Determine the prefix for the section
    if section == "A":
        prefix = "A0_"
    elif section == "B":
        prefix = "B0_"
    else:  # section == "C"
        prefix = "C"
    
    # Query documents where question_id starts with the section prefix
    questions = list(collection.find({"question_id": {"$regex": f"^{prefix}"}}))
    return [ESGQuestion.parse_obj(question) for question in questions]
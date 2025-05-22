from fastapi import APIRouter, HTTPException
from typing import List
from models import ESGQuestion, ESGQuestionUpdate
from services.questionService import (
    create_or_update_question,
    bulk_upload_questions,
    get_question,
    update_question_response,
    get_questions_by_section,
)

router = APIRouter()

@router.post("/question/", response_model=ESGQuestion)
async def create_or_update_question_endpoint(question: ESGQuestion):
    return create_or_update_question(question)

@router.post("/questions/", response_model=List[ESGQuestion])
async def bulk_upload_questions_endpoint(questions: List[ESGQuestion]):
    return bulk_upload_questions(questions)

@router.get("/questions/{question_id}", response_model=ESGQuestion)
async def get_question_endpoint(question_id: str):
    return get_question(question_id)

@router.put("/questions/{question_id}", response_model=ESGQuestion)
async def update_question_response_endpoint(question_id: str, update: ESGQuestionUpdate):
    return update_question_response(question_id, update)

@router.get("/questions/section/{section}", response_model=List[ESGQuestion])
async def get_questions_by_section_endpoint(section: str):
    return get_questions_by_section(section)
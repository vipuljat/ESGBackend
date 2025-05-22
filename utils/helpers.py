from fastapi import HTTPException

def parse_question_id(question_id: str) -> str:
    if question_id.startswith("A0"):
        return "A"
    elif question_id.startswith("B0"):
        return "B"
    elif question_id.startswith("C"):
        return "C"
    else:
        raise HTTPException(status_code=400, detail="Invalid question_id format")
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from app.models import AssignmentCreate, AssignmentInDB, SubmissionInDB, UserInDB
from app.database import db
from app.auth import get_current_active_user
from bson import ObjectId
import shutil
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/assignments/", response_model=AssignmentInDB)
async def create_assignment(assignment: AssignmentCreate, current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "teacher" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    
    # Verify class ownership
    classroom = await db.classrooms.find_one({"_id": ObjectId(assignment.class_id)})
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    if classroom["teacher_id"] != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized for this class")

    assignment_dict = assignment.dict()
    assignment_dict["created_at"] = datetime.utcnow()
    
    new_assignment = await db.assignments.insert_one(assignment_dict)
    created_assignment = await db.assignments.find_one({"_id": new_assignment.inserted_id})
    return AssignmentInDB(**created_assignment)

@router.get("/classes/{class_id}/assignments", response_model=List[AssignmentInDB])
async def list_assignments(class_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    # Verify membership
    classroom = await db.classrooms.find_one({"_id": ObjectId(class_id)})
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    
    user_id = str(current_user.id)
    if user_id not in classroom["students"] and classroom["teacher_id"] != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not a member of this class")

    assignments = await db.assignments.find({"class_id": class_id}).to_list(100)
    return [AssignmentInDB(**a) for a in assignments]

@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: str, 
    file: UploadFile = File(...), 
    current_user: UserInDB = Depends(get_current_active_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")

    assignment = await db.assignments.find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Save file
    file_location = f"{UPLOAD_DIR}/{assignment_id}_{current_user.id}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    submission_dict = {
        "assignment_id": assignment_id,
        "student_id": str(current_user.id),
        "file_path": file_location,
        "filename": file.filename,
        "submitted_at": datetime.utcnow()
    }
    
    await db.submissions.insert_one(submission_dict)
    return {"message": "Submission uploaded successfully"}

@router.get("/assignments/{assignment_id}/submissions", response_model=List[SubmissionInDB])
async def list_submissions(assignment_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "teacher" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")
        
    submissions = await db.submissions.find({"assignment_id": assignment_id}).to_list(100)
    return [SubmissionInDB(**s) for s in submissions]

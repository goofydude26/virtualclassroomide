from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models import ClassroomCreate, ClassroomInDB, UserInDB, JoinRequest
from app.database import db
from app.auth import get_current_active_user
from bson import ObjectId
import uuid

router = APIRouter()

@router.post("/classes/", response_model=ClassroomInDB)
async def create_class(classroom: ClassroomCreate, current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "teacher" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only teachers can create classes")
    
    class_dict = classroom.dict()
    class_dict["teacher_id"] = str(current_user.id)
    class_dict["class_code"] = str(uuid.uuid4())[:8] # Simple 8-char code
    class_dict["students"] = []
    class_dict["pending_requests"] = []

    new_class = await db.classrooms.insert_one(class_dict)
    created_class = await db.classrooms.find_one({"_id": new_class.inserted_id})
    return ClassroomInDB(**created_class)

@router.get("/classes", response_model=List[ClassroomInDB])
async def list_classes(current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role == "admin":
        classes = await db.classrooms.find().to_list(100)
    elif current_user.role == "teacher":
        classes = await db.classrooms.find({"teacher_id": str(current_user.id)}).to_list(100)
    else:
        # Student: only classes they are enrolled in
        classes = await db.classrooms.find({"students": str(current_user.id)}).to_list(100)
    return [ClassroomInDB(**c) for c in classes]

@router.get("/classes/pending", response_model=List[ClassroomInDB])
async def get_pending_requests(current_user: UserInDB = Depends(get_current_active_user)):
    # For teachers, show classes where they are the teacher and have pending requests
    if current_user.role == "teacher":
        classes = await db.classrooms.find({"teacher_id": str(current_user.id), "pending_requests": {"$ne": []}}).to_list(100)
        return [ClassroomInDB(**c) for c in classes]
    return []

@router.get("/classes/{class_id}", response_model=ClassroomInDB)
async def get_class(class_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    classroom = await db.classrooms.find_one({"_id": ObjectId(class_id)})
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassroomInDB(**classroom)

@router.post("/classes/join")
async def join_class(request: JoinRequest, current_user: UserInDB = Depends(get_current_active_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can join classes")
    
    classroom = await db.classrooms.find_one({"class_code": request.class_code})
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Check if already joined or pending
    user_id = str(current_user.id)
    if user_id in classroom["students"]:
        return {"message": "Already enrolled"}
    if user_id in classroom["pending_requests"]:
        return {"message": "Request already pending"}
    
    await db.classrooms.update_one(
        {"_id": classroom["_id"]},
        {"$push": {"pending_requests": user_id}}
    )
    return {"message": "Join request sent"}

@router.post("/classes/{class_id}/approve")
async def approve_student(class_id: str, student_id: str, current_user: UserInDB = Depends(get_current_active_user)):
    classroom = await db.classrooms.find_one({"_id": ObjectId(class_id)})
    if not classroom:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if classroom["teacher_id"] != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to approve for this class")
    
    if student_id not in classroom["pending_requests"]:
        raise HTTPException(status_code=400, detail="Student not in pending requests")
    
    # Move from pending to students
    await db.classrooms.update_one(
        {"_id": ObjectId(class_id)},
        {
            "$pull": {"pending_requests": student_id},
            "$push": {"students": student_id}
        }
    )
    return {"message": "Student approved"}


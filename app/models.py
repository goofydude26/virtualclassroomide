from pydantic import BaseModel, EmailStr, Field, ConfigDict, GetJsonSchemaHandler
from typing import List, Optional, Any
from bson import ObjectId
from pydantic_core import core_schema
from datetime import datetime

# Helper for MongoDB ObjectId handling
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> Any:
        return handler(core_schema.str_schema())

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# --- Authentication Models ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "student" # student, teacher, admin
    admin_secret_key: Optional[str] = None # Required if role is admin

class UserLogin(BaseModel):
    username: EmailStr # OAuth2PasswordRequestForm uses 'username'
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class UserInDB(MongoBaseModel):
    email: EmailStr
    hashed_password: str
    role: str

class UserResponse(MongoBaseModel):
    email: EmailStr
    role: str

# --- Course/Classroom Models ---

class ClassroomCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ClassroomInDB(MongoBaseModel):
    name: str
    description: Optional[str] = None
    teacher_id: str # User ID of the teacher
    students: List[str] = [] # List of Student User IDs
    pending_requests: List[str] = [] # List of Student User IDs waiting for approval
    class_code: str # Unique code for joining

class JoinRequest(BaseModel):
    class_code: str

# --- Assignment Models ---

class AssignmentCreate(BaseModel):
    class_id: str
    title: str
    description: str
    due_date: Optional[str] = None

class AssignmentInDB(MongoBaseModel):
    class_id: str
    title: str
    description: str
    due_date: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SubmissionInDB(MongoBaseModel):
    assignment_id: str
    student_id: str
    file_path: str
    filename: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

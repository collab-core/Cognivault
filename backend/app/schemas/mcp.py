from pydantic import BaseModel


class McpSelection(BaseModel):
    programme_id: str
    semester: int
    regulation_year: int


class McpGroundRequest(BaseModel):
    selection: McpSelection
    course_id: str
    user_prompt: str


class McpCourseOption(BaseModel):
    id: str
    code: str
    name: str
    semester: int
    regulation_year: int


class McpGroundResponse(BaseModel):
    course_id: str
    course_code: str
    relevant: bool
    reason: str
    augmented_prompt: str | None = None


class McpChatResponse(BaseModel):
    course_id: str
    course_code: str
    relevant: bool
    reason: str
    answer: str | None = None

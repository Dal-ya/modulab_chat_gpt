from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str]
    data: Optional[T]


class ResponseImage(BaseModel):
    url: str


class PaintDTO(BaseModel):
    success: bool
    message: str
    data: list[ResponseImage] | dict


class CreatePaintDTO(BaseModel):
    author: str
    description: str


class CreateFineTuneNameDTO(BaseModel):
    name: str


class RequestChatByFineTuneDTO(BaseModel):
    fineTuneModel: str
    prompt: str

from pydantic import BaseModel


class ResponseImage(BaseModel):
    url: str


class PaintDTO(BaseModel):
    success: bool
    message: str
    data: list[ResponseImage] | dict


class CreatePaintDTO(BaseModel):
    author: str
    description: str

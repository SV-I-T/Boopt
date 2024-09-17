from bson import ObjectId
from pydantic import BaseModel, Field


class Video(BaseModel):
    id_: ObjectId = Field(alias="_id")
    vid: str
    titulo: str

    class Config:
        arbitrary_types_allowed = True

    @property
    def thumbnail_url(self):
        return f"https://vumbnail.com/{self.vid}.jpg"

    @property
    def url(self):
        return f"https://vimeo.com/{self.vid}"


video_teste = Video(_id=ObjectId(), titulo="A PONTE", vid="152509858")

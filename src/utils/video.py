from bson import ObjectId
from pydantic import BaseModel, Field

from utils.banco_dados import db


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

    @classmethod
    def consultar(cls, id_video: ObjectId | str):
        r = db("VelaVideos").find_one({"_id": ObjectId(id_video)})
        if r:
            return Video(**r)
        return None


video_teste = Video(
    _id=ObjectId("66ec52fda7a0c251dde79b78"), titulo="A PONTE", vid="152509858"
)

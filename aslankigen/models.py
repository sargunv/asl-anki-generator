from pydantic import BaseModel


class WordSet(BaseModel):
    tags: list[str]
    words: list[str]


class Group(BaseModel):
    name: str
    sets: list[WordSet]


class WordsConfig(BaseModel):
    name: str
    export_filename: str
    groups: list[Group]

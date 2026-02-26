from pydantic import BaseModel


class WordsConfig(BaseModel):
    name: str
    export_filename: str
    words: list[str]

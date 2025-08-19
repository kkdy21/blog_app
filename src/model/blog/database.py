from dataclasses import dataclass
from datetime import datetime


@dataclass
class BlogData:
    id: int
    title: str
    author_id: str
    content: str
    modified_dt: datetime
    image_loc: str

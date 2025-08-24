from dataclasses import dataclass
from datetime import datetime


@dataclass
class BlogData:
    id: int
    title: str
    author: str
    author_id: int
    content: str
    created_at: datetime
    modified_dt: datetime
    image_loc: str

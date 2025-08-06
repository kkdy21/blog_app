from fastapi import Form


class CreateBlogRequest:
    def __init__(
        self,
        title: str = Form(...),
        author: str = Form(...),
        content: str = Form(...),
        image_loc: str | None = Form(None),
    ):
        self.title = title
        self.author = author
        self.content = content
        self.image_loc = image_loc

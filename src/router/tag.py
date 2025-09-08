from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.tag.response import TagResponse
from src.service.tag_svc import TagService
from src.utils.db.db import get_db_session

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
async def get_tags(
    blog_id: int, session: AsyncSession = Depends(get_db_session)
) -> list[TagResponse]:
    tags = await TagService().get_tags_by_blog_id(blog_id, session)
    return [TagResponse.model_validate(tag) for tag in tags]


@router.delete("/delete/{tag_id}")
async def delete_tag(
    tag_id: int, session: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    await TagService().delete_tag(tag_id, session)
    return JSONResponse(
        content={"message": "Tag deleted successfully"}, status_code=status.HTTP_200_OK
    )


@router.post("/create")
async def create_tag(
    tag_names: list[str], session: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    await TagService().create_tags(tag_names, session)
    return JSONResponse(
        content={"message": "Tag created successfully"}, status_code=status.HTTP_200_OK
    )

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.model.blog.orm import Blog
from src.model.tag.orm import Tag


class TagService:
    async def create_tags(
        self, tag_names: list[str], session: AsyncSession
    ) -> list[Tag]:
        """
        태그 이름 목록을 받아, 존재하지 않는 태그는 생성하고
        모든 태그의 ORM 객체 리스트를 반환합니다.
        """
        if not tag_names:
            return []

        # 1. 한 번의 쿼리로 이미 존재하는 태그들을 모두 조회합니다.
        stmt = select(Tag).where(Tag.name.in_(tag_names))
        result = await session.execute(stmt)
        existing_tags = list(result.scalars().all())
        existing_tag_names = {tag.name for tag in existing_tags}

        # 2. DB에 존재하지 않는 새로운 태그 이름들을 찾습니다.
        new_tag_names = set(tag_names) - existing_tag_names

        # 3. 새로운 태그들을 생성합니다.
        new_tags = []
        if new_tag_names:
            for name in new_tag_names:
                new_tag = Tag(name=name)
                session.add(new_tag)
                new_tags.append(new_tag)
            # flush를 한 번만 호출하여 모든 새 태그를 DB에 반영하고 ID를 할당받습니다.
            await session.flush()

        # 4. 기존 태그와 새로 생성된 태그를 합쳐서 반환합니다.
        return existing_tags + new_tags

    async def get_tags_by_blog_id(
        self, blog_id: int, session: AsyncSession
    ) -> list[Tag]:
        stmt = select(Tag).join(Blog).where(Blog.id == blog_id)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    # delete tag
    async def delete_tag(self, tag_id: int, session: AsyncSession) -> None:
        stmt = delete(Tag).where(Tag.id == tag_id)  # noqa: F821
        await session.execute(stmt)
        await session.commit()

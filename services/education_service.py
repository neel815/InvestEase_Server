from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.concept import Concept
from schemas.concept import ConceptOut


async def get_all_concepts(db: AsyncSession) -> list[ConceptOut]:
    result = await db.execute(
        select(Concept).order_by(Concept.order_index.asc(), Concept.title.asc())
    )
    concepts = result.scalars().all()

    return [
        ConceptOut(
            id=concept.id,
            title=concept.title,
            summary=concept.description,
            explanation=concept.explanation or concept.description,
            number_example=concept.number_example or "Example coming soon.",
            created_at=concept.created_at,
        )
        for concept in concepts
    ]

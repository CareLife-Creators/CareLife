from app.application.use_cases.impact import ImpactService
from app.infrastructure.repositories.impact import PostgresImpactRepository


def get_impact_service() -> ImpactService:
    return ImpactService(PostgresImpactRepository())
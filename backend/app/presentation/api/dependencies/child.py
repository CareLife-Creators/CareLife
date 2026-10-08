from app.application.use_cases.children import ChildService
from app.infrastructure.repositories.child import PostgresChildRepository


def get_child_service() -> ChildService:
    return ChildService(PostgresChildRepository())
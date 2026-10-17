from app.application.use_cases.remote_checkins import (
    RemoteCheckInService,
)
from app.infrastructure.repositories.remote_checkins import (
    PostgresRemoteCheckInRepository,
)


def get_remote_checkin_service() -> RemoteCheckInService:
    return RemoteCheckInService(
        repository=PostgresRemoteCheckInRepository(),
    )
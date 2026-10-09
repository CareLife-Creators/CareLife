from app.application.interfaces.impact import ImpactRepository
from app.domain.entities.impact import (
ImpactMedia,
ImpactMediaType,
ImpactUpdate,
ImpactUpdateStatus,
)
from app.infrastructure.database.connection import get_connection

_UPDATE_SELECT = """
SELECT iu.id, iu.organization_id, o.name, iu.title, iu.content,
iu.status, iu.created_by, iu.reviewed_by, iu.review_notes,
iu.created_at, iu.updated_at, iu.reviewed_at, iu.published_at
FROM impact_updates iu
JOIN organizations o ON o.id = iu.organization_id
"""

_MEDIA_SELECT = """
SELECT id, update_id, storage_key, content_type,
media_type, file_size, created_at
FROM impact_media
"""

_STAFF_ACCESS_SELECT = """
SELECT 1
FROM organizations o
JOIN user_organizations uo ON uo.organization_id = o.id
JOIN users u ON u.id = uo.user_id
JOIN roles r ON r.id = u.role_id
WHERE o.id = %s
AND o.organization_type = 'orphanage'
AND u.id = %s
AND u.is_active = TRUE
AND r.name = 'orphanage_staff'
"""

class PostgresImpactRepository(ImpactRepository):
"""Persistence and organization-access checks for impact updates."""

```
@staticmethod
def _assert_staff_access(
    connection,
    organization_id: str,
    user_id: str,
) -> None:
    row = connection.execute(
        _STAFF_ACCESS_SELECT + " FOR SHARE OF o, uo, u",
        (organization_id, user_id),
    ).fetchone()

    if row is None:
        raise PermissionError(
            "Authorized orphanage staff membership is required"
        )

def is_authorized_orphanage_staff(
    self,
    organization_id: str,
    user_id: str,
) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            _STAFF_ACCESS_SELECT,
            (organization_id, user_id),
        ).fetchone()

    return row is not None

def create_update(self, update: ImpactUpdate) -> ImpactUpdate:
    with get_connection() as connection:
        with connection.transaction():
            self._assert_staff_access(
                connection,
                update.organization_id,
                update.created_by,
            )

            connection.execute(
                """
                INSERT INTO impact_updates (
                    id, organization_id, title, content, status,
                    created_by, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    update.id,
                    update.organization_id,
                    update.title,
                    update.content,
                    update.status.value,
                    update.created_by,
                    update.created_at,
                    update.updated_at,
                ),
            )

    saved = self.get_update(update.id)
    if saved is None:
        raise RuntimeError(
            "Impact update was created but could not be reloaded"
        )

    return saved

def get_update(self, update_id: str) -> ImpactUpdate | None:
    with get_connection() as connection:
        row = connection.execute(
            _UPDATE_SELECT + " WHERE iu.id = %s",
            (update_id,),
        ).fetchone()

    return self._update_from_row(row)

def list_public_updates(
    self,
    organization_id: str | None = None,
) -> list[ImpactUpdate]:
    query = (
        _UPDATE_SELECT
        + """
        JOIN verification_statuses vs ON vs.id = o.status_id
        WHERE iu.status = 'approved'
          AND o.organization_type = 'orphanage'
          AND vs.name = 'verified'
        """
    )
    params: list[object] = []

    if organization_id is not None:
        query += " AND iu.organization_id = %s"
        params.append(organization_id)

    query += " ORDER BY iu.published_at DESC, iu.created_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        update
        for row in rows
        if (update := self._update_from_row(row)) is not None
    ]

def list_pending_updates(self) -> list[ImpactUpdate]:
    query = (
        _UPDATE_SELECT
        + """
        WHERE iu.status = 'pending_review'
          AND o.organization_type = 'orphanage'
        ORDER BY iu.created_at ASC
        """
    )

    with get_connection() as connection:
        rows = connection.execute(query).fetchall()

    return [
        update
        for row in rows
        if (update := self._update_from_row(row)) is not None
    ]

def add_media(
    self,
    organization_id: str,
    user_id: str,
    media: ImpactMedia,
) -> ImpactMedia:
    with get_connection() as connection:
        with connection.transaction():
            # Check the identity of the person uploading the media.
            self._assert_staff_access(
                connection,
                organization_id,
                user_id,
            )

            update_row = connection.execute(
                """
                SELECT 1
                FROM impact_updates
                WHERE id = %s
                  AND organization_id = %s
                  AND status = 'pending_review'
                FOR UPDATE
                """,
                (media.update_id, organization_id),
            ).fetchone()

            if update_row is None:
                raise ValueError(
                    "Media can only be added to a pending update "
                    "belonging to this organization"
                )

            connection.execute(
                """
                INSERT INTO impact_media (
                    id, update_id, storage_key, content_type,
                    media_type, file_size, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    media.id,
                    media.update_id,
                    media.storage_key,
                    media.content_type,
                    media.media_type.value,
                    media.file_size,
                    media.created_at,
                ),
            )

    with get_connection() as connection:
        row = connection.execute(
            _MEDIA_SELECT + " WHERE id = %s",
            (media.id,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Media was saved but could not be reloaded")

    result = self._media_from_row(row)
    if result is None:
        raise RuntimeError("Media was saved but could not be reloaded")

    return result

def list_media(self, update_id: str) -> list[ImpactMedia]:
    with get_connection() as connection:
        rows = connection.execute(
            _MEDIA_SELECT
            + " WHERE update_id = %s ORDER BY created_at ASC",
            (update_id,),
        ).fetchall()

    return [
        media
        for row in rows
        if (media := self._media_from_row(row)) is not None
    ]

def review_update(
    self,
    update_id: str,
    decision: str,
    reviewer_id: str,
    review_notes: str | None,
) -> ImpactUpdate | None:
    with get_connection() as connection:
        with connection.transaction():
            row = connection.execute(
                """
                SELECT status
                FROM impact_updates
                WHERE id = %s
                FOR UPDATE
                """,
                (update_id,),
            ).fetchone()

            if row is None:
                return None

            if row[0] != ImpactUpdateStatus.PENDING_REVIEW.value:
                raise ValueError(
                    "Only pending impact updates can be reviewed"
                )

            connection.execute(
                """
                UPDATE impact_updates
                SET status = %s,
                    reviewed_by = %s,
                    review_notes = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    published_at = CASE
                        WHEN %s = 'approved'
                        THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    decision,
                    reviewer_id,
                    review_notes,
                    decision,
                    update_id,
                ),
            )

    return self.get_update(update_id)

def get_public_media(self, media_id: str) -> ImpactMedia | None:
    query = (
        """
        SELECT m.id, m.update_id, m.storage_key, m.content_type,
               m.media_type, m.file_size, m.created_at
        FROM impact_media m
        JOIN impact_updates iu ON iu.id = m.update_id
        JOIN organizations o ON o.id = iu.organization_id
        JOIN verification_statuses vs ON vs.id = o.status_id
        WHERE m.id = %s
          AND iu.status = 'approved'
          AND o.organization_type = 'orphanage'
          AND vs.name = 'verified'
        """
    )

    with get_connection() as connection:
        row = connection.execute(query, (media_id,)).fetchone()

    return self._media_from_row(row)

@staticmethod
def _update_from_row(row) -> ImpactUpdate | None:
    if row is None:
        return None

    return ImpactUpdate(
        id=row[0],
        organization_id=row[1],
        organization_name=row[2],
        title=row[3],
        content=row[4],
        status=ImpactUpdateStatus(row[5]),
        created_by=row[6],
        reviewed_by=row[7],
        review_notes=row[8],
        created_at=row[9],
        updated_at=row[10],
        reviewed_at=row[11],
        published_at=row[12],
    )

@staticmethod
def _media_from_row(row) -> ImpactMedia | None:
    if row is None:
        return None

    return ImpactMedia(
        id=row[0],
        update_id=row[1],
        storage_key=row[2],
        content_type=row[3],
        media_type=ImpactMediaType(row[4]),
        file_size=row[5],
        created_at=row[6],
    )
```

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.child import (
    ChildContactRequest,
    ChildContactResponse,
    ChildCreateRequest,
    ChildResponse,
    ChildUpdateRequest,
    OutcomeCreateRequest,
    OutcomeResponse,
    OutcomeUpdateRequest,
)
from app.application.use_cases.children import ChildService
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.child import get_child_service


router = APIRouter(
    prefix="/children",
    tags=["Child Profiles"],
)


def child_response(child) -> ChildResponse:
    return ChildResponse(
        id=child.id,
        full_name=child.full_name,
        date_of_birth=child.date_of_birth,
        gender=child.gender,
        allergies=child.allergies,
        medical_notes=child.medical_notes,
        parent_id=child.parent_id,
        orphanage_organization_id=child.orphanage_organization_id,
        daycare_organization_id=child.daycare_organization_id,
    )


def contact_response(contact) -> ChildContactResponse:
    return ChildContactResponse(
        id=contact.id,
        child_id=contact.child_id,
        contact_type=contact.contact_type,
        full_name=contact.full_name,
        relationship_to_child=contact.relationship_to_child,
        phone=contact.phone,
        email=contact.email,
        address=contact.address,
        created_at=contact.created_at.isoformat(),
        updated_at=contact.updated_at.isoformat(),
    )


def outcome_response(outcome) -> OutcomeResponse:
    return OutcomeResponse(
        id=outcome.id,
        child_id=outcome.child_id,
        organization_id=outcome.organization_id,
        outcome_type=outcome.outcome_type,
        outcome_status=outcome.outcome_status,
        outcome_date=outcome.outcome_date,
        notes=outcome.notes,
        created_by=outcome.created_by,
        created_at=outcome.created_at.isoformat(),
        updated_at=outcome.updated_at.isoformat(),
    )


# ============================================================
# CAR-113 DAYCARE CHILD PROFILE ROUTES
# Keep these BEFORE /{child_id} routes.
# ============================================================

@router.post(
    "/daycare",
    response_model=ChildResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_daycare_child(
    request: ChildCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        child = service.create_daycare_child(
            current_user,
            request,
        )
        return child_response(child)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/daycare",
    response_model=list[ChildResponse],
)
def list_daycare_children(
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        children = service.list_daycare_children(current_user)
        return [child_response(child) for child in children]
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/daycare/{child_id}",
    response_model=ChildResponse,
)
def get_daycare_child(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        child = service.get_daycare_child(
            current_user,
            child_id,
        )
        return child_response(child)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.put(
    "/daycare/{child_id}",
    response_model=ChildResponse,
)
def update_daycare_child(
    child_id: str,
    request: ChildUpdateRequest,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        child = service.update_daycare_child(
            current_user,
            child_id,
            request,
        )
        return child_response(child)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/daycare/{child_id}/emergency-contacts",
    response_model=ChildContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_emergency_contact(
    child_id: str,
    request: ChildContactRequest,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        contact = service.add_emergency_contact(
            current_user,
            child_id,
            request,
        )
        return contact_response(contact)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/daycare/{child_id}/emergency-contacts",
    response_model=list[ChildContactResponse],
)
def list_emergency_contacts(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        contacts = service.list_emergency_contacts(
            current_user,
            child_id,
        )
        return [
            contact_response(contact)
            for contact in contacts
        ]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/daycare/{child_id}/pickup-persons",
    response_model=ChildContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_pickup_person(
    child_id: str,
    request: ChildContactRequest,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        contact = service.add_pickup_person(
            current_user,
            child_id,
            request,
        )
        return contact_response(contact)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/daycare/{child_id}/pickup-persons",
    response_model=list[ChildContactResponse],
)
def list_pickup_persons(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.DAYCARE_STAFF,
        )
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        contacts = service.list_pickup_persons(
            current_user,
            child_id,
        )
        return [
            contact_response(contact)
            for contact in contacts
        ]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


# ============================================================
# Existing CAR-55 / CAR-57 ORPHANAGE ROUTES
# ============================================================

@router.post(
    "/orphanages/{organization_id}/children",
    response_model=ChildResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_child(
    organization_id: str,
    request: ChildCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.ORPHANAGE_STAFF)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        return child_response(
            service.create(
                current_user,
                organization_id,
                request,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/orphanages/{organization_id}",
    response_model=list[ChildResponse],
)
def list_children(
    organization_id: str,
    current_user: UserContext = Depends(
        require_role(Role.ORPHANAGE_STAFF)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        children = service.list_children(
            current_user,
            organization_id,
        )
        return [
            child_response(child)
            for child in children
        ]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/{child_id}",
    response_model=ChildResponse,
)
def get_child(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.ORPHANAGE_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        return child_response(
            service.get(
                current_user,
                child_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.put(
    "/{child_id}",
    response_model=ChildResponse,
)
def update_child(
    child_id: str,
    request: ChildUpdateRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.ORPHANAGE_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        return child_response(
            service.update(
                current_user,
                child_id,
                request,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{child_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_child(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.ORPHANAGE_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        service.delete(
            current_user,
            child_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/{child_id}/outcomes",
    response_model=OutcomeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_outcome(
    child_id: str,
    request: OutcomeCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.ORPHANAGE_STAFF)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        return outcome_response(
            service.create_outcome(
                current_user,
                child_id,
                request,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/{child_id}/outcomes",
    response_model=list[OutcomeResponse],
)
def list_outcomes(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.ORPHANAGE_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        outcomes = service.list_outcomes(
            current_user,
            child_id,
        )
        return [
            outcome_response(outcome)
            for outcome in outcomes
        ]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/outcomes/{outcome_id}",
    response_model=OutcomeResponse,
)
def get_outcome(
    outcome_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.ORPHANAGE_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        return outcome_response(
            service.get_outcome(
                current_user,
                outcome_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.put(
    "/outcomes/{outcome_id}",
    response_model=OutcomeResponse,
)
def update_outcome(
    outcome_id: str,
    request: OutcomeUpdateRequest,
    current_user: UserContext = Depends(
        require_role(Role.ORPHANAGE_STAFF)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        return outcome_response(
            service.update_outcome(
                current_user,
                outcome_id,
                request,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.delete(
    "/outcomes/{outcome_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_outcome(
    outcome_id: str,
    current_user: UserContext = Depends(
        require_role(Role.ORPHANAGE_STAFF)
    ),
    service: ChildService = Depends(get_child_service),
):
    try:
        service.delete_outcome(
            current_user,
            outcome_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
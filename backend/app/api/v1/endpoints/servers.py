from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....db import get_db
from ....models import Server, User
from ....schemas import ServerCreate, ServerUpdate, ServerResponse
from ....services import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ServerResponse])
async def list_servers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve list of servers.
    """
    servers = db.query(Server).offset(skip).limit(limit).all()
    return servers


@router.post("/", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_in: ServerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new server.
    """
    server = Server(**server_in.dict())
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


@router.get("/{server_id}", response_model=ServerResponse)
async def get_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get server by ID.
    """
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )
    return server


@router.patch("/{server_id}", response_model=ServerResponse)
async def update_server(
    server_id: int,
    server_in: ServerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a server.
    """
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    update_data = server_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(server, field, value)

    db.commit()
    db.refresh(server)
    return server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a server.
    """
    server = db.query(Server).filter(Server.id == server_id).first()
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found"
        )

    db.delete(server)
    db.commit()
    return None

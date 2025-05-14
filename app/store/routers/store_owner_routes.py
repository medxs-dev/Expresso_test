from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union
from app.core.db import get_db
from typing import Any
from app.store.schemas.store_owner_schema import (
    StoreOwnerBase,
    StoreOwnerResponse
)
from app.store.services.store_owner_service import (
    create_store_owner,
    get_all_store_owners,
    get_store_owner_by_id,
    update_store_owner,
    delete_store_owner,
    get_store_owners_search_by_name,
    get_store_owner_details_by_id,
    get_store_owner_detailss_by_id
)
from app.common.utils.response import success_response, error_response, Response
from app.common.exceptions.exceptions import NotFoundException, DatabaseException
router = APIRouter(
    prefix="/v1/store-owners",
    tags=["Store Owners"]
)


@router.post("/", summary="Create a new store owner", response_model=Response)
async def create_owner(
    data: StoreOwnerBase,
    db: AsyncSession = Depends(get_db)
):
    try:
        store_owner = await create_store_owner(data, db)  # ✅ Corrected order
        response_data = StoreOwnerResponse.model_validate(store_owner)
        return success_response("Store owner created successfully", response_data)
    except HTTPException as e:
        return error_response("Failed to create store owner", {"error": e.detail})


@router.get("/", summary="Get all store owners", response_model=Response)
async def get_list_owner(db: AsyncSession = Depends(get_db)):
    try:
        owners = await get_all_store_owners(db)
        # validated = [StoreOwnerResponse.model_validate(
        #     owner) for owner in owners]
        return success_response("Store owners fetched successfully", owners)
    except Exception as e:
        return error_response("Failed to fetch store !!", {"error": str(e)})


@router.get("/search", summary="Search store owners by name", response_model=Response)
async def get_store_owners(
    search_term: str = "",
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        owners = await get_store_owners_search_by_name(db, search_term, limit, offset)
        return success_response("Store owner search successful", owners)
    except Exception as e:
        return error_response("Failed to search store owners", {"error": str(e)})


@router.get("/{owner_id}", summary="Get store owner by ID", response_model=Response)
async def get_owner(owner_id: int, db: AsyncSession = Depends(get_db)):
    try:
        owner = await get_store_owner_by_id(owner_id, db)
        validated = StoreOwnerResponse.model_validate(owner)
        return success_response("Store owner fetched successfully", validated)
    except HTTPException as e:
        return error_response("Store owner not found", {"error": e.detail})
    except Exception as e:
        return error_response("Failed to fetch store owner", {"error": str(e)})


@router.put("/{owner_id}", summary="Update store owner", response_model=Response)
async def update_owner(owner_id: int, store_owner: StoreOwnerBase, db: AsyncSession = Depends(get_db)):
    try:
        updated_owner = await update_store_owner(owner_id, store_owner, db)
        validated = StoreOwnerResponse.model_validate(updated_owner)
        return success_response("Store owner updated successfully", validated)
    except HTTPException as e:
        return error_response("Store owner not found", {"error": e.detail})
    except Exception as e:
        return error_response("Failed to update store owner", {"error": str(e)})


@router.delete("/{owner_id}", summary="Delete store owner", response_model=Response)
async def delete_owner(owner_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted_owner = await delete_store_owner(owner_id, db)
        validated = StoreOwnerResponse.model_validate(deleted_owner)
        return success_response("Store owner deleted successfully", validated)
    except HTTPException as e:
        return error_response("Store owner not found", {"error": e.detail})
    except Exception as e:
        return error_response("Failed to delete store owner", {"error": str(e)})


@router.get("/details/{owner_id}", response_model=Response)
async def get_store_owner_details(owner_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await get_store_owner_details_by_id(owner_id, db)
        return success_response("Store owner details fetched successfully", result)

    except NotFoundException as e:
        return error_response(str(e), {"code": "OWNER_NOT_FOUND"})

    except DatabaseException as e:
        return error_response("Internal server error while accessing the database", {"code": "DB_ERROR"})

    except Exception as e:
        # Log unexpected errors
        return error_response("Unexpected server error", {"detail": str(e), "code": "UNEXPECTED_ERROR"})


@router.get("/detailss/{owner_id}", response_model=Response)
async def get_store_owner_details(owner_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await get_store_owner_detailss_by_id(owner_id, db)
        return success_response("Store owner details fetched successfully", result)

    except NotFoundException as e:
        return error_response(str(e), {"code": "OWNER_NOT_FOUND"})

    except DatabaseException as e:
        return error_response("Internal server error while accessing the database", {"code": "DB_ERROR"})

    except Exception as e:
        # Log unexpected errors
        return error_response("Unexpected server error", {"detail": str(e), "code": "UNEXPECTED_ERROR"})

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.store.models.store_models import StoreOwnerModel
from app.store.schemas.store_owner_schema import StoreOwnerBase
from datetime import date, datetime
from fastapi import HTTPException, status
from app.common.utils.dynamic_search import dynamic_search
from app.common.utils.response import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.common.exceptions.exceptions import DatabaseException, NotFoundException


def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


async def create_store_owner(store_owner: StoreOwnerBase, db: AsyncSession):

    age = calculate_age(store_owner.dob)

    insert_query = text("""
        INSERT INTO exp_store_owners (
            full_name,
            dob,
            gender_id,
            age,
            email,
            mobile,
            phone,
            current_addr,
            permanent_addr,
            created_by
        ) VALUES (
            :full_name,
            :dob,
            :gender_id,
            :age,
            :email,
            :mobile,
            :phone,
            :current_addr,
            :permanent_addr,
            :created_by
        )
        RETURNING
            id,
            full_name,
            dob,
            gender_id,
            age,
            email,
            mobile,
            phone,
            current_addr,
            permanent_addr,
            created_by,
            created_on
    """)

    try:
        result = await db.execute(insert_query, {
            "full_name": store_owner.full_name,
            "dob": store_owner.dob,
            "gender_id": store_owner.gender_id,
            "age": age,
            "email": store_owner.email,
            "mobile": store_owner.mobile,
            "phone": store_owner.phone,
            "current_addr": store_owner.current_addr,
            "permanent_addr": store_owner.permanent_addr,
            "created_by": store_owner.created_by
        })

        await db.commit()
        row = result.fetchone()

        if row:
            return dict(row._mapping)

        raise HTTPException(
            status_code=500, detail="Failed to insert store owner.")

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")


async def get_all_store_owners(db: AsyncSession):
    query = text("""
        SELECT eo.id, eo.full_name, eo.age, eo.email, eo.dob, eo.mobile, eo.current_addr, eo.created_by, 
               eo.created_on, eg.gender_name, eg.is_active
        FROM public.exp_store_owners eo
        JOIN exp_gender_master eg ON eg.id = eo.gender_id
        WHERE eg.is_active = true
    """)

    try:
        result = await db.execute(query)
        rows = result.fetchall()

        if not rows:
            raise NotFoundException("Store owner not found")

        return [dict(row._mapping) for row in rows]

    except SQLAlchemyError as e:
        raise DatabaseException("Database query failed")


async def get_store_owner_by_id(owner_id: int, db: AsyncSession):
    result = await db.execute(select(StoreOwnerModel).filter_by(id=owner_id))
    owner = result.scalar_one_or_none()
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Store owner not found.")
    return owner


async def update_store_owner(owner_id: int, store_owner: StoreOwnerBase, db: AsyncSession):
    # Calculate age
    age = calculate_age(store_owner.dob)

    query = text("""
        UPDATE public.exp_store_owners
        SET 
            full_name = :full_name,
            dob = :dob,
            gender_id = :gender_id,
            age = :age,
            email = :email,
            mobile = :mobile,
            phone = :phone,
            current_addr = :current_addr,
            permanent_addr = :permanent_addr,
            updated_by = :updated_by,
            updated_on = :updated_on
        WHERE id = :owner_id
        RETURNING *;
    """)

    try:
        result = await db.execute(query, {
            "full_name": store_owner.full_name,
            "dob": store_owner.dob,
            "gender_id": store_owner.gender_id,
            "age": age,
            "email": store_owner.email,
            "mobile": store_owner.mobile,
            "phone": store_owner.phone,
            "current_addr": store_owner.current_addr,
            "permanent_addr": store_owner.permanent_addr,
            "updated_by": store_owner.updated_by,
            "updated_on": datetime.utcnow(),
            "owner_id": owner_id
        })

        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=500, detail="Store owner not found.")

        await db.commit()
        return dict(row._mapping)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update store owner: {str(e)}"
        )


async def delete_store_owner(owner_id: int, db: AsyncSession):
    query = text("""
        DELETE FROM exp_store_owners
        WHERE id = :owner_id
        RETURNING *;
    """)

    params = {"owner_id": owner_id}

    try:
        result = await db.execute(query, params)
        deleted_owner = result.fetchone()

        if not deleted_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store owner not found."
            )

        await db.commit()  # ✅ This line is critical

        return dict(deleted_owner._mapping)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete store owner: {str(e)}"
        )


async def get_store_owners_search_by_name(
    db: AsyncSession,
    search_term: str = "",
    limit: int = 10,
    offset: int = 0
):
    store_owners = await dynamic_search(
        db=db,
        table_name="exp_store_owners",
        search_fields=["full_name"],
        search_term=search_term,
        limit=limit,
        offset=offset
    )
    return store_owners


async def get_store_owner_details_by_id(owner_id: int, db: AsyncSession):
    query = text("""
        SELECT eo.id, eo.email, eo.mobile, eg.gender_name
        FROM public.exp_store_owners eo
        JOIN exp_gender_master eg ON eg.id = eo.gender_id
        WHERE eo.id = :owner_id
    """)

    try:
        result = await db.execute(query, {"owner_id": owner_id})
        row = result.fetchone()

        if not row:
            raise NotFoundException(
                f"Store owner with id {owner_id} not found")

        return dict(row._mapping)

    except SQLAlchemyError as e:
        # Log the error here (e.g., logger.error(str(e)))
        raise DatabaseException("Database query failed")


async def get_store_owner_detailss_by_id(owner_id: int, db: AsyncSession):
    query = text("""
        SELECT eo.id, eo.email, eo.mobile, eg.is_active,  eg.gender_name
        FROM public.exp_store_owners eo
        JOIN exp_gender_master eg ON eg.id = eo.gender_id
        WHERE eo.id = :owner_id  
    """)

    try:
        result = await db.execute(query, {"owner_id": owner_id})
        row = result.fetchone()

        if not row:
            raise NotFoundException(
                f"Store owner with id {owner_id} not found")

        return dict(row._mapping)

    except SQLAlchemyError as e:
        # Log the error here (e.g., logger.error(str(e)))
        raise DatabaseException("Database query failed")

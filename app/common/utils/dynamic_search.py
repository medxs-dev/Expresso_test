from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from typing import List, Optional, Dict

# ✅ Define allowed tables and their fields
ALLOWED_TABLES = {
    "exp_store_owners": [
        "id", "full_name", "email", "mobile", "phone", "dob", "age",
        "gender_id", "current_addr", "permanent_addr", "updated_by", "updated_on"
    ]
}


def validate_table_name(table_name: str) -> str:
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")
    return table_name


def validate_field_names(table_name: str, fields: List[str]) -> List[str]:
    allowed = ALLOWED_TABLES[table_name]
    for field in fields:
        if field not in allowed:
            raise ValueError(
                f"Invalid field '{field}' for table '{table_name}'")
    return fields


async def dynamic_search(
    db: AsyncSession,
    table_name: str,
    search_fields: List[str],
    search_term: str = "",
    limit: int = 10,
    offset: int = 0,
    additional_filters: Optional[Dict[str, any]] = None
):
    # ✅ Validate
    table_name = validate_table_name(table_name)
    search_fields = validate_field_names(table_name, search_fields)
    if additional_filters:
        validate_field_names(table_name, list(additional_filters.keys()))

    # ✅ Start query construction
    sql = f"SELECT * FROM {table_name}"
    where_clauses = []
    params = {}

    # Search filter
    if search_term and search_fields:
        ilike_clauses = []
        for idx, field in enumerate(search_fields):
            param_key = f"search_{idx}"
            ilike_clauses.append(f"{field} ILIKE :{param_key}")
            params[param_key] = f"%{search_term}%"
        where_clauses.append("(" + " OR ".join(ilike_clauses) + ")")

    # Additional filters
    if additional_filters:
        for key, value in additional_filters.items():
            param_key = f"filter_{key}"
            where_clauses.append(f"{key} = :{param_key}")
            params[param_key] = value

    # Combine WHERE clause
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    sql += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset

    # ✅ Execute
    stmt = text(sql)
    result = await db.execute(stmt, params)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

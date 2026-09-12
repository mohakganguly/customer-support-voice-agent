from datetime import datetime, timezone

from backend.database import get_connection


def save_memory(
    customer_id: str,
    key: str,
    value: str,
    category: str,
) -> dict:
    """
    Create or update a memory for a customer.

    Memories are uniquely identified by:
        customer_id + key
    """

    now = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    try:
        existing = connection.execute(
            """
            SELECT memory_id
            FROM memories
            WHERE customer_id = ?
              AND key = ?
            """,
            (customer_id, key),
        ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE memories
                SET value = ?,
                    category = ?,
                    updated_at = ?
                WHERE memory_id = ?
                """,
                (
                    value,
                    category,
                    now,
                    existing["memory_id"],
                ),
            )

            memory_id = existing["memory_id"]

        else:
            cursor = connection.execute(
                """
                INSERT INTO memories (
                    customer_id,
                    key,
                    value,
                    category,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    key,
                    value,
                    category,
                    now,
                    now,
                ),
            )

            memory_id = cursor.lastrowid

        connection.commit()

        return {
            "memory_id": memory_id,
            "customer_id": customer_id,
            "key": key,
            "value": value,
            "category": category,
            "updated_at": now,
        }

    finally:
        connection.close()


def get_memories(customer_id: str) -> list[dict]:
    """
    Retrieve all memories belonging to a customer.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                memory_id,
                customer_id,
                key,
                value,
                category,
                created_at,
                updated_at
            FROM memories
            WHERE customer_id = ?
            ORDER BY updated_at DESC
            """,
            (customer_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def delete_memory(
    customer_id: str,
    key: str,
) -> bool:
    """
    Delete a specific memory belonging to a customer.

    Returns True if a memory was deleted,
    otherwise False.
    """

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM memories
            WHERE customer_id = ?
              AND key = ?
            """,
            (customer_id, key),
        )

        connection.commit()

        return cursor.rowcount > 0



    finally:
        connection.close()

def search_memories(customer_id: str, query: str) -> list[dict]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                memory_id,
                customer_id,
                key,
                value,
                category,
                created_at,
                updated_at
            FROM memories
            WHERE customer_id = ?
              AND (
                    LOWER(key) LIKE ?
                    OR LOWER(value) LIKE ?
                    OR LOWER(category) LIKE ?
              )
            ORDER BY updated_at DESC
            """,
            (
                customer_id,
                f"%{query.lower()}%",
                f"%{query.lower()}%",
                f"%{query.lower()}%",
            ),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()
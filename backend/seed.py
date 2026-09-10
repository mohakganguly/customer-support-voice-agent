from backend.database import get_connection
from backend.models import create_tables


def seed_database() -> None:
    """
    Populate the database with sample customer-support data.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # =========================================================
    # CUSTOMERS
    # =========================================================

    cursor.executemany(
        """
        INSERT OR IGNORE INTO customers
        (customer_id, name, email, phone)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                "CUS-1001",
                "Mohak",
                "mohak@example.com",
                "+91-9876543210",
            ),
            (
                "CUS-1002",
                "Rahul",
                "rahul@example.com",
                "+91-9876500000",
            ),
        ],
    )

    # =========================================================
    # SUBSCRIPTIONS
    # =========================================================

    cursor.executemany(
        """
        INSERT OR IGNORE INTO subscriptions
        (
            subscription_id,
            customer_id,
            plan,
            status,
            price,
            billing_cycle,
            next_billing_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "SUB-5001",
                "CUS-1001",
                "Pro",
                "active",
                49.99,
                "monthly",
                "2026-10-01",
            ),
            (
                "SUB-5002",
                "CUS-1002",
                "Basic",
                "active",
                19.99,
                "monthly",
                "2026-10-15",
            ),
        ],
    )

    # =========================================================
    # ORDERS
    # =========================================================

    cursor.executemany(
        """
        INSERT OR IGNORE INTO orders
        (
            order_id,
            customer_id,
            status,
            carrier,
            tracking_number,
            estimated_delivery
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "ORD-0001",
                "CUS-1001",
                "shipped",
                "NovaExpress",
                "NX123456789",
                "tomorrow",
            ),
            (
                "ORD-0002",
                "CUS-1001",
                "processing",
                None,
                None,
                "2026-09-14",
            ),
            (
                "ORD-0003",
                "CUS-1002",
                "delivered",
                "NovaExpress",
                "NX987654321",
                "2026-09-08",
            ),
        ],
    )

    # =========================================================
    # PAYMENTS
    # =========================================================

    cursor.executemany(
        """
        INSERT OR IGNORE INTO payments
        (
            transaction_id,
            customer_id,
            amount,
            currency,
            status,
            description,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "PAY-7001",
                "CUS-1001",
                49.99,
                "USD",
                "completed",
                "NovaTech Pro monthly subscription",
                "2026-09-01T10:00:00",
            ),
            (
                "PAY-7002",
                "CUS-1001",
                49.99,
                "USD",
                "completed",
                "Duplicate NovaTech Pro subscription charge",
                "2026-09-01T10:01:00",
            ),
            (
                "PAY-8001",
                "CUS-1002",
                19.99,
                "USD",
                "completed",
                "NovaTech Basic monthly subscription",
                "2026-09-01T11:00:00",
            ),
        ],
    )

    connection.commit()
    connection.close()

    print("Database seeded successfully.")


if __name__ == "__main__":
    create_tables()
    seed_database()
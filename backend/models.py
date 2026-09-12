from backend.database import get_connection


def create_tables() -> None:
    """
    Create all application tables.
    """

    connection = get_connection()

    cursor = connection.cursor()

    # CUSTOMERS

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT
        )
        """
    )

    # SUBSCRIPTIONS

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            plan TEXT NOT NULL,
            status TEXT NOT NULL,
            price REAL NOT NULL,
            billing_cycle TEXT NOT NULL,
            next_billing_date TEXT,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
        """
    )

    # ORDERS

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            status TEXT NOT NULL,
            carrier TEXT,
            tracking_number TEXT,
            estimated_delivery TEXT,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
        """
    )

    # PAYMENTS

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            transaction_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            timestamp TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
        """
    )

    # SUPPORT TICKETS

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            issue TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        )
        """
    )

    # REFUNDS

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS refunds (
            refund_id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id),

            FOREIGN KEY (transaction_id)
                REFERENCES payments(transaction_id)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()
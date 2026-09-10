from datetime import datetime
from typing import Any

from backend.database import get_connection


# CUSTOMERS

def get_customer_by_email(email: str) -> dict[str, Any] | None:
    """
    Find a customer using their email address.
    """

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            customer_id,
            name,
            email,
            phone
        FROM customers
        WHERE LOWER(email) = LOWER(?)
        """,
        (email.strip(),),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# SUBSCRIPTIONS

def get_subscription_by_customer(
    customer_id: str,
) -> dict[str, Any] | None:
    """
    Find the subscription belonging to a customer.
    """

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            subscription_id,
            customer_id,
            plan,
            status,
            price,
            billing_cycle,
            next_billing_date
        FROM subscriptions
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# ORDERS

def get_order(
    order_id: str,
) -> dict[str, Any] | None:
    """
    Find an order by order ID.
    """

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            order_id,
            customer_id,
            status,
            carrier,
            tracking_number,
            estimated_delivery
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# PAYMENTS

def get_payment(
    transaction_id: str,
) -> dict[str, Any] | None:
    """
    Find a payment by transaction ID.
    """

    connection = get_connection()

    row = connection.execute(
        """
        SELECT
            transaction_id,
            customer_id,
            amount,
            currency,
            status,
            description,
            timestamp
        FROM payments
        WHERE transaction_id = ?
        """,
        (transaction_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# SUPPORT TICKETS

def create_ticket(
    customer_id: str,
    issue: str,
    priority: str = "normal",
) -> dict[str, Any]:

    connection = get_connection()

    # Generate ticket ID
    row = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM tickets
        """
    ).fetchone()

    ticket_number = 10001 + row["count"]

    ticket_id = f"TKT-{ticket_number}"

    created_at = datetime.utcnow().isoformat()

    connection.execute(
        """
        INSERT INTO tickets
        (
            ticket_id,
            customer_id,
            issue,
            status,
            priority,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_id,
            customer_id,
            issue,
            "open",
            priority,
            created_at,
        ),
    )

    connection.commit()

    ticket = connection.execute(
        """
        SELECT
            ticket_id,
            customer_id,
            issue,
            status,
            priority,
            created_at
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,),
    ).fetchone()

    connection.close()

    return dict(ticket)


# REFUNDS

def create_refund(
    transaction_id: str,
    reason: str,
) -> dict[str, Any]:

    connection = get_connection()

    # First check the payment exists
    payment = connection.execute(
        """
        SELECT
            transaction_id,
            customer_id,
            amount,
            currency
        FROM payments
        WHERE transaction_id = ?
        """,
        (transaction_id,),
    ).fetchone()

    if payment is None:
        connection.close()
        raise ValueError("Payment not found.")

    # Check whether refund already exists
    existing_refund = connection.execute(
        """
        SELECT *
        FROM refunds
        WHERE transaction_id = ?
        """,
        (transaction_id,),
    ).fetchone()

    if existing_refund is not None:
        connection.close()
        raise ValueError(
            "A refund has already been requested for this payment."
        )

    # Generate refund ID
    row = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM refunds
        """
    ).fetchone()

    refund_id = f"REF-{10001 + row['count']}"

    created_at = datetime.utcnow().isoformat()

    connection.execute(
        """
        INSERT INTO refunds
        (
            refund_id,
            transaction_id,
            customer_id,
            amount,
            currency,
            reason,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            refund_id,
            transaction_id,
            payment["customer_id"],
            payment["amount"],
            payment["currency"],
            reason,
            "requested",
            created_at,
        ),
    )

    connection.commit()

    refund = connection.execute(
        """
        SELECT *
        FROM refunds
        WHERE refund_id = ?
        """,
        (refund_id,),
    ).fetchone()

    connection.close()

    return dict(refund)
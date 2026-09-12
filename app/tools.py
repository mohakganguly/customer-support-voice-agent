import re
from typing import Any

from livekit.agents import RunContext, function_tool

from backend.repository import (
    get_customer_by_email,
    get_subscription_by_customer,
    get_order,
    get_payment,
    create_ticket,
    create_refund,
)
from backend.memory_repository import (
    save_memory,
    get_memories,
    delete_memory,
    search_memories,
)

# ORDER ID NORMALIZATION

NUMBER_WORDS = {
    "ZERO": "0",
    "ONE": "1",
    "TWO": "2",
    "THREE": "3",
    "FOUR": "4",
    "FIVE": "5",
    "SIX": "6",
    "SEVEN": "7",
    "EIGHT": "8",
    "NINE": "9",
}


def normalize_order_id(order_id: str) -> str:
    """
    Normalize written or spoken order IDs.

    Examples:

        ORD-0001
        ORD 0001
        order 0001
        0001
        zero zero zero one

    become:

        ORD-0001
    """

    text = order_id.strip().upper()

    words = text.split()

    converted = []

    for word in words:
        if word in NUMBER_WORDS:
            converted.append(NUMBER_WORDS[word])
        else:
            converted.append(word)

    text = " ".join(converted)

    # Remove spoken words
    text = re.sub(r"\bORDER\b", "", text)
    text = re.sub(r"\bORD\b", "", text)
    text = re.sub(r"\bHYPHEN\b", "", text)

    # Extract numeric characters
    digits = "".join(re.findall(r"\d", text))

    if digits:
        return f"ORD-{digits.zfill(4)}"

    return order_id.strip().upper()

def normalize_payment_id(payment_id: str) -> str:
    """
    Normalize written or spoken payment IDs.

    Examples:

        PAY-7002
        PAY 7002
        payment 7002
        7002
        seven zero zero two

    become:

        PAY-7002
    """

    text = payment_id.strip().upper()

    words = text.split()

    converted = []

    for word in words:
        if word in NUMBER_WORDS:
            converted.append(NUMBER_WORDS[word])
        else:
            converted.append(word)

    text = " ".join(converted)

    # Remove common spoken words
    text = re.sub(r"\bPAYMENT\b", "", text)
    text = re.sub(r"\bPAY\b", "", text)
    text = re.sub(r"\bHYPHEN\b", "", text)

    # Extract numeric characters
    digits = "".join(re.findall(r"\d", text))

    if digits:
        return f"PAY-{digits.zfill(4)}"

    return payment_id.strip().upper()

# TOOL 1 — CHECK CUSTOMER

@function_tool
async def check_customer(
    context: RunContext,
    email: str,
) -> dict[str, Any]:
    """
    Look up a NovaTech customer using their email address.

    Use this when you need to identify a customer's account.
    """

    customer = get_customer_by_email(email)

    if customer is None:
        return {
            "success": False,
            "error": "customer_not_found",
            "message": (
                "No NovaTech customer account was found "
                "for this email."
            ),
        }
    context.userdata.customer_id = customer["customer_id"]
    context.userdata.customer_email = customer["email"]
    context.userdata.customer_name = customer["name"]

    return {
        "success": True,
        "customer": customer,
    }


# TOOL 2 — GET SUBSCRIPTION

@function_tool
async def get_subscription(
    context: RunContext,
    customer_id: str,
) -> dict[str, Any]:
    """
    Retrieve the subscription associated with a customer.
    """

    subscription = get_subscription_by_customer(customer_id)

    if subscription is None:
        return {
            "success": False,
            "error": "subscription_not_found",
            "message": (
                "No subscription was found "
                "for this customer."
            ),
        }

    return {
        "success": True,
        "subscription": subscription,
    }


# TOOL 3 — GET ORDER STATUS

@function_tool
async def get_order_status(
    context: RunContext,
    order_id: str,
) -> dict[str, Any]:
    """
    Retrieve the current status and delivery information
    for an order.
    """

    normalized_id = normalize_order_id(order_id)

    order = get_order(normalized_id)

    if order is None:
        return {
            "success": False,
            "error": "order_not_found",
            "message": (
                f"No order was found with ID {normalized_id}."
            ),
        }

    return {
        "success": True,
        "order_id": normalized_id,
        "order": order,
    }


# TOOL 4 — CHECK PAYMENT

@function_tool
async def check_payment(
    context: RunContext,
    payment_id: str,
) -> dict[str, Any]:
    """
    Retrieve payment information for a transaction.

    The payment ID may be provided in written or spoken form.
    """

    transaction_id = normalize_payment_id(payment_id)

    payment = get_payment(transaction_id)

    if payment is None:
        return {
            "success": False,
            "error": "payment_not_found",
            "message": (
                f"No payment was found with ID "
                f"{transaction_id}."
            ),
        }

    return {
        "success": True,
        "transaction_id": transaction_id,
        "payment": payment,
    }

# TOOL 5 — CREATE SUPPORT TICKET

@function_tool
async def create_support_ticket(
    context: RunContext,
    customer_id: str,
    issue: str,
) -> dict[str, Any]:
    """
    Create a support ticket for a customer.
    """

    try:
        ticket = create_ticket(
            customer_id=customer_id,
            issue=issue,
        )

        return {
            "success": True,
            "ticket": ticket,
            "message": (
                f"Support ticket {ticket['ticket_id']} "
                f"has been created."
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": "ticket_creation_failed",
            "message": str(e),
        }


# TOOL 6 — REQUEST REFUND

@function_tool
async def request_refund(
    context: RunContext,
    payment_id: str,
    reason: str,
) -> dict[str, Any]:
    """
    Request a refund for a payment.

    Only use this when the customer explicitly requests
    a refund and a valid payment ID is available.
    """

    transaction_id = normalize_payment_id(payment_id)

    try:
        refund = create_refund(
            transaction_id=transaction_id,
            reason=reason,
        )

        return {
            "success": True,
            "refund": refund,
            "message": (
                f"Refund request {refund['refund_id']} "
                f"has been created for "
                f"{refund['amount']} "
                f"{refund['currency']}."
            ),
        }

    except ValueError as e:
        return {
            "success": False,
            "error": "refund_failed",
            "message": str(e),
        }

    except Exception as e:
        return {
            "success": False,
            "error": "refund_system_error",
            "message": str(e),
        }


 #SAVE MEMORY TOOL

@function_tool
async def save_customer_memory(
    context: RunContext,
    key: str,
    value: str,
    category: str,
) -> dict:
    """
    Save a useful piece of information about the current customer.

    Use this only when the information is genuinely useful for
    future customer-support conversations.
    """

    customer_id = context.userdata.customer_id

    if not customer_id:
        return {
            "success": False,
            "error": "customer_not_identified",
        }

    memory = save_memory(
        customer_id=customer_id,
        key=key,
        value=value,
        category=category,
    )

    return {
        "success": True,
        "memory": memory,
    }

# RETRIEVE MEMORY TOOL

@function_tool
async def get_customer_memories(
    context: RunContext,
) -> dict:
    """
    Retrieve memories associated with the current customer.
    """

    customer_id = context.userdata.customer_id

    if not customer_id:
        return {
            "success": False,
            "error": "customer_not_identified",
        }

    memories = get_memories(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "memories": memories,
    }

#DELETE MEMORY TOOL

@function_tool
async def delete_customer_memory(
    context: RunContext,
    key: str,
) -> dict:
    """
    Delete a specific memory belonging to the current customer.
    """

    customer_id = context.userdata.customer_id

    if not customer_id:
        return {
            "success": False,
            "error": "customer_not_identified",
        }

    deleted = delete_memory(
        customer_id=customer_id,
        key=key,
    )

    return {
        "success": deleted,
        "key": key,
    }

# SEARCH CUSTOMER MEMORIES

@function_tool
async def search_customer_memories(
    context: RunContext,
    query: str,
) -> dict:
    """
    Search the current customer's memories for information
    relevant to the current conversation.
    """

    customer_id = context.userdata.customer_id

    if not customer_id:
        return {
            "success": False,
            "error": "customer_not_identified",
        }

    memories = search_memories(
        customer_id=customer_id,
        query=query,
    )

    return {
        "success": True,
        "customer_id": customer_id,
        "memories": memories,
    }
from dataclasses import dataclass


@dataclass
class SupportSessionState:
    customer_id: str | None = None
    customer_email: str | None = None
    customer_name: str | None = None


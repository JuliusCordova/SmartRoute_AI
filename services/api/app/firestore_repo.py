"""Firestore Standard adapter; ADC and bounded reads, no cloud at import time."""
from .orders import Order, OrderPage
from .firestore_config import firestore_client


class FirestoreOrderRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def create(self, order: Order) -> None:
        self.db.collection("orders").document(order.id).create(order.model_dump(mode="python"))

    def list(self, *, limit: int, after: str | None) -> OrderPage:
        coll = self.db.collection("orders")
        query = coll.order_by("__name__")
        if after:
            prior = coll.document(after).get()
            if not prior.exists:
                raise ValueError("Invalid pagination cursor")
            query = query.start_after(prior)
        docs = list(query.limit(limit + 1).stream())
        has_more = len(docs) > limit
        selected = docs[:limit]
        return OrderPage(
            items=[Order.model_validate(doc.to_dict()) for doc in selected],
            next_cursor=selected[-1].id if has_more and selected else None,
        )

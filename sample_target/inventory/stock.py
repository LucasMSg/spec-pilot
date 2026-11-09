class OutOfStockError(Exception):
    pass


class Inventory:
    def __init__(self):
        self._items: dict[str, int] = {}

    def add(self, sku: str, qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._items[sku] = self._items.get(sku, 0) + qty

    def remove(self, sku: str, qty: int) -> None:
        current = self._items.get(sku, 0)
        if qty > current:
            raise OutOfStockError(f"{sku}: have {current}, need {qty}")
        self._items[sku] = current - qty
        if self._items[sku] == 0:
            del self._items[sku]

    def count(self, sku: str) -> int:
        return self._items.get(sku, 0)

    def low_stock(self, threshold: int = 5) -> list[str]:
        return sorted(s for s, q in self._items.items() if q < threshold)
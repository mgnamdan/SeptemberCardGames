"""Play chips only: no real money, exchange rates, or purchases."""
from dataclasses import dataclass


@dataclass
class Wallet:
    balance: int = 1000

    def spend(self, amount):
        if amount <= 0 or amount > self.balance:
            raise ValueError("Not enough chips")
        self.balance -= amount

    def credit(self, amount):
        if amount < 0:
            raise ValueError("Cannot credit negative chips")
        self.balance += amount

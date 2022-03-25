from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum


class Transaction(ABC):

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class Transfer(Transaction):

    def __init__(self):
        self.out_of: Account
        self.to: Account
        self.amount: int
        self.currency: Currency

    def validate(self):
        assert self.out_of
        assert self.to
        assert self.amount and self.amount > 0
        assert self.currency
        assert self.out_of.currency is self.to.currency and self.currency is self.out_of.currency

    def execute(self):
        self.out_of.withdraw(self.amount)
        self.to.deposit(self.amount)


class Currency(Enum):
    EURO = "EURO"
    DOLLAR = "DOLLAR"


class Identifier(ABC):

    @abstractmethod
    def equals(self, other_identifier: Identifier):
        pass


class IBAN(Identifier):

    def __init__(self, iban: str):
        self.iban = iban

    def equals(self, other_identifier: Identifier):
        return isinstance(other_identifier, IBAN) and self.iban is other_identifier.iban


class Account:

    def __init__(self, identifier: Identifier, currency: Currency = Currency.EURO):
        self.identifier = identifier
        self.balance = 0
        self.currency = currency

    @staticmethod
    def identified_by(identifier: Identifier) -> Account:
        return Account(identifier)

    def withdraw(self, amount: int):
        self.balance = self.balance - amount

    def deposit(self, amount: int):
        self.balance = self.balance + amount


class TransferBuilder:

    def __init__(self, transfer: Transfer):
        self.transfer = transfer

    @staticmethod
    def transfer(amount: int, currency: Currency) -> TransferBuilder:
        t = Transfer()
        t.amount = amount
        t.currency = currency
        return TransferBuilder(transfer=t)

    def out_of(self, account: Account) -> TransferBuilder:
        self.transfer.out_of = account
        return self

    def to(self, account: Account) -> TransferBuilder:
        self.transfer.to = account
        return self

    def create(self):
        self.transfer.validate()
        return self.transfer


if __name__ == '__main__':

    account_transfer = TransferBuilder.transfer(100, Currency.EURO).out_of(
        Account.identified_by(IBAN("DE89370400440532013000"))).to(
        Account.identified_by(IBAN("DE89370400440532013000"))).create()
    account_transfer.execute()

    assert account_transfer.out_of.balance == -100
    assert account_transfer.to.balance == 100

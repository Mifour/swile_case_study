import enum
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, Enum, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class TypeEnum(enum.StrEnum):
    payment = "PAYMENT"


class StatusEnum(enum.StrEnum):
    captured = "CAPTURED"
    declined = "DECLINED"
    refunded = "REFUNDED"


class Base(DeclarativeBase):
    pass


class Transaction(Base):
    __tablename__ = "transaction"
    id: Mapped[uuid4] = mapped_column(Uuid, primary_key=True)
    type: Mapped[TypeEnum] = mapped_column(Enum(TypeEnum))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    wallet_id: Mapped[uuid4] = mapped_column(Uuid)
    siret: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f"Transaction(id={self.id}, wallet={self.wallet_id}, at={self.created_at.isoformat()})"

    def validate_values(self) -> bool:
        try:
            TypeEnum(self.type)
            StatusEnum(self.status)
        except ValueError as e:
            print(f"{e} from values {self.__dict__}")
            return False
        return True


class Shop(Base):
    __tablename__ = "shop"
    siret: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    naf_code: Mapped[str] = mapped_column(String(6))

    def __repr__(self) -> str:
        return f"Shop(siret={self.siret})"

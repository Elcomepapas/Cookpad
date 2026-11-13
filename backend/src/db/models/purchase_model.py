from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from src.db.connection import Base


class Purchase(Base):
    __tablename__ = "compra"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(
        Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    comercio = Column(String(120), nullable=False)
    fecha_compra = Column(Date, nullable=False)
    productos = relationship(
        "FridgeItem", back_populates="compra", cascade="all, delete-orphan"
    )


class FridgeItem(Base):
    __tablename__ = "heladera_producto"

    id = Column(Integer, primary_key=True)
    compra_id = Column(
        Integer, ForeignKey("compra.id", ondelete="CASCADE"), nullable=False
    )
    ingrediente_id = Column(
        Integer, ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False
    )
    nombre_producto = Column(String(200), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_total = Column(Numeric(10, 2), nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    compra = relationship("Purchase", back_populates="productos")

    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_heladera_producto_cantidad"),
        CheckConstraint("precio_total >= 0", name="ck_heladera_producto_precio"),
    )

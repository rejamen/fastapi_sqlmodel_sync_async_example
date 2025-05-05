from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from pydantic import computed_field


class Contact(SQLModel):
    name: str
    email: str


class ContactDB(Contact, table=True):
    __tablename__ = "contact"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    

class Product(SQLModel):
    name: str
    

class ProductDB(Product, table=True):
    __tablename__ = "product"
    
    id: Optional[int] = Field(default=None, primary_key=True)


class OrderTagRelDB(SQLModel, table=True):
    __tablename__ = "order_tag_rel"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    tag_id: int = Field(foreign_key="tag.id")


class Order(SQLModel):
    name: str
    contact_id: int


class OrderDB(Order, table=True):
    __tablename__ = "order"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_lines: List["OrderLineDB"] = Relationship(back_populates="order")
    tags: List["TagDB"] = Relationship(back_populates="orders", link_model=OrderTagRelDB)


class OrderLineDB(SQLModel, table=True):
    __tablename__ = "order_line"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", ondelete="CASCADE")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    price: float
    order: "OrderDB" = Relationship(back_populates="order_lines")


class OrderLineCreate(SQLModel):
    product_id: int
    quantity: int
    price: float


class OrderLineRead(SQLModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(Order):
    order_lines: List[OrderLineCreate]
    tag_ids: List[int] = []

    
class OrderRead(SQLModel):
    id: int
    name: str
    contact_id: int
    order_lines: List[OrderLineRead] = []
    tags: List["Tag"] = []
    
    @computed_field
    def amount_total(self) -> float:
        total = sum(line.price * line.quantity for line in self.order_lines)
        return round(total, 2)


class Tag(SQLModel):
    name: str


class TagDB(Tag, table=True):
    __tablename__ = "tag"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    orders: List["OrderDB"] = Relationship(back_populates="tags", link_model=OrderTagRelDB)

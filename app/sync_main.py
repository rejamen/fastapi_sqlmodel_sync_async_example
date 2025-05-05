import logging
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, APIRouter
from typing import Generator, List

from app.database import engine
from app.models import (
    Contact, ContactDB,
    Product, ProductDB,
    Tag, TagDB,
    OrderDB, OrderCreate, OrderRead,
    OrderLineDB,
    OrderTagRelDB
)

_logger = logging.getLogger("uvicorn")

sync_router = APIRouter(prefix="/sync")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

@sync_router.post("/contact")
def create_contact(contact: Contact, session: Session = Depends(get_session)):
    try:
        contact_db = ContactDB(**contact.model_dump())
        session.add(contact_db)
        session.commit()
        session.refresh(contact_db)
        return contact_db
    except Exception as e:
        _logger.error(f"Error creating contact: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@sync_router.get("/contact")
def get_contacts(session: Session = Depends(get_session)):
    try:
        query = select(ContactDB)
        contacts = session.exec(query).all()
        return contacts
    except Exception as e:
        _logger.error(f"Error fetching contacts: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@sync_router.post("/product")
def create_product(product: Product, session: Session = Depends(get_session)):
    try:
        product_db = ProductDB(**product.model_dump())
        session.add(product_db)
        session.commit()
        session.refresh(product_db)
        return product_db
    except Exception as e:
        _logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@sync_router.get("/product")
def get_products(session: Session = Depends(get_session)):
    try:
        query = select(ProductDB)
        products = session.exec(query).all()
        return products
    except Exception as e:
        _logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@sync_router.post("/tag")
def create_order_tag(tag: Tag, session: Session = Depends(get_session)):
    try:
        tag_db = TagDB(**tag.model_dump())
        session.add(tag_db)
        session.commit()
        session.refresh(tag_db)
        return tag_db
    except Exception as e:
        _logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@sync_router.get("/tag")
def get_tags(session: Session = Depends(get_session)):
    try:
        query = select(TagDB)
        tags = session.exec(query).all()
        return tags
    except Exception as e:
        _logger.error(f"Error fetching tags: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@sync_router.post('/order')
def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    try:
        # Create order without the order_lines (since that's a relationship, not a column)
        order_data = order.model_dump(exclude={"order_lines"})
        order_db = OrderDB(**order_data)
        session.add(order_db)
        session.flush()  # Flush to get the order ID
        
        # Create the OrderLine records
        for line in order.order_lines:
            order_line = OrderLineDB(
                order_id=order_db.id,
                product_id=line.product_id,
                quantity=line.quantity,
                price=line.price
            )
            session.add(order_line)
        
        # Add tags to order
        for tag_id in order.tag_ids:
            # Get tag from database
            tag = session.get(TagDB, tag_id)
            if tag:
                # Create relationship in OrderTagRelDB
                order_tag_rel = OrderTagRelDB(order_id=order_db.id, tag_id=tag_id)
                session.add(order_tag_rel)
        
        # Commit all changes at once
        session.commit()
        session.refresh(order_db)  # Refresh to load the relationships
        return order_db
    except Exception as e:
        _logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@sync_router.get('/order', response_model=List[OrderRead])
def get_orders(session: Session = Depends(get_session)):
    try:
        query = select(OrderDB)
        orders = session.exec(query).all()
        for order in orders:
            # Force load the relationships - SQLModel will handle this automatically when returning
            order.order_lines
            order.tags
        return orders
    except Exception as e:
        _logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

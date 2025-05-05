import logging
from sqlmodel import select
from fastapi import HTTPException, APIRouter, Depends
from typing import List, AsyncGenerator
from sqlalchemy.orm import sessionmaker, selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import async_engine
from app.models import (
    Contact, ContactDB,
    Product, ProductDB,
    Tag, TagDB,
    OrderDB, OrderCreate, OrderRead,
    OrderLineDB,
    OrderTagRelDB
)

_logger = logging.getLogger("uvicorn")

async_router = APIRouter(prefix="/async")

async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@async_router.post("/contact")
async def create_contact(contact: Contact, session: AsyncSession = Depends(get_async_session)):
    try:
        contact_db = ContactDB(**contact.model_dump())
        session.add(contact_db)
        await session.commit()
        await session.refresh(contact_db)
        return contact_db
    except Exception as e:
        _logger.error(f"Error creating contact: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@async_router.get("/contact")
async def get_contacts(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(ContactDB)
        result = await session.exec(query)
        contacts = result.all()
        return contacts
    except Exception as e:
        _logger.error(f"Error fetching contacts: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@async_router.post("/product")
async def create_product(product: Product, session: AsyncSession = Depends(get_async_session)):
    try:
        product_db = ProductDB(**product.model_dump())
        session.add(product_db)
        await session.commit()
        await session.refresh(product_db)
        return product_db
    except Exception as e:
        _logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@async_router.get("/product")
async def get_products(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(ProductDB)
        result = await session.exec(query)
        products = result.all()
        return products
    except Exception as e:
        _logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@async_router.post("/tag")
async def create_order_tag(tag: Tag, session: AsyncSession = Depends(get_async_session)):
    try:
        tag_db = TagDB(**tag.model_dump())
        session.add(tag_db)
        await session.commit()
        await session.refresh(tag_db)
        return tag_db
    except Exception as e:
        _logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@async_router.get("/tag")
async def get_tags(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(TagDB)
        result = await session.exec(query)
        tags = result.all()
        return tags
    except Exception as e:
        _logger.error(f"Error fetching tags: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")

@async_router.post('/order')
async def create_order(order: OrderCreate, session: AsyncSession = Depends(get_async_session)):
    try:
        # Create order without the order_lines (since that's a relationship, not a column)
        order_data = order.model_dump(exclude={"order_lines"})
        order_db = OrderDB(**order_data)
        session.add(order_db)
        await session.flush()  # Flush to get the order ID
        
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
            tag = await session.get(TagDB, tag_id)
            if tag:
                # Create relationship in OrderTagRelDB
                order_tag_rel = OrderTagRelDB(order_id=order_db.id, tag_id=tag_id)
                session.add(order_tag_rel)
        
        # Commit all changes at once
        await session.commit()
        await session.refresh(order_db)  # Refresh to load the relationships
        return order_db
    except Exception as e:
        _logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@async_router.get('/order', response_model=List[OrderRead])
async def get_orders(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(OrderDB).options(
            selectinload(OrderDB.order_lines),
            selectinload(OrderDB.tags),
        )
        result = await session.exec(query)
        orders = result.all()
        for order in orders:
            # Force load the relationships - SQLModel will handle this automatically when returning
            order.order_lines
            order.tags
        return orders
    except Exception as e:
        _logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

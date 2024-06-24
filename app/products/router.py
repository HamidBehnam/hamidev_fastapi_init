from fastapi import APIRouter

products_router = APIRouter()


@products_router.get("/")
async def read_products():
    return [{"name": "Product 1"}, {"name": "Product 2"}]

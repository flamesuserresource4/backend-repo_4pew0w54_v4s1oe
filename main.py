import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents, db
from schemas import Product, Category, Order, Wishlist, User

app = FastAPI(title="Shop API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Shop API running"}

@app.get("/api/schema")
def get_schema_info():
    # Simple heartbeat plus signal that schemas exist
    return {"collections": ["user", "category", "product", "order", "wishlist"]}

# ---------------- Products ----------------

@app.get("/api/products")
def list_products(q: Optional[str] = None, category: Optional[str] = None, brand: Optional[str] = None,
                  min_price: Optional[float] = None, max_price: Optional[float] = None, limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    query = {}
    if q:
        # Basic case-insensitive search on title
        query["title"] = {"$regex": q, "$options": "i"}
    if category:
        query["category"] = category
    if brand:
        query["brand"] = brand
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["price"] = price_filter

    docs = get_documents("product", query, limit)
    # Convert ObjectId to string for frontend friendliness
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

class AddProductRequest(Product):
    pass

@app.post("/api/products")
def create_product(product: AddProductRequest):
    pid = create_document("product", product)
    return {"id": pid}

# ---------------- Categories ----------------

@app.get("/api/categories")
def list_categories(limit: int = 100):
    docs = get_documents("category", {}, limit)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

@app.post("/api/categories")
def create_category(category: Category):
    cid = create_document("category", category)
    return {"id": cid}

# ---------------- Wishlist ----------------

@app.get("/api/wishlist")
def get_wishlist(user_email: str, limit: int = 100):
    docs = get_documents("wishlist", {"user_email": user_email}, limit)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

@app.post("/api/wishlist")
def add_to_wishlist(item: Wishlist):
    wid = create_document("wishlist", item)
    return {"id": wid}

# ---------------- Orders ----------------

@app.get("/api/orders")
def list_orders(user_email: str, limit: int = 50):
    docs = get_documents("order", {"user_email": user_email}, limit)
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}

@app.post("/api/orders")
def create_order(order: Order):
    oid = create_document("order", order)
    return {"id": oid}

# ---------------- Health / Test ----------------

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

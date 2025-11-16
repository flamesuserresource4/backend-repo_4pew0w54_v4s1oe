"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Category(BaseModel):
    """Product categories"""
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly identifier")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category (slug)")
    brand: Optional[str] = Field(None, description="Brand name")
    image: Optional[str] = Field(None, description="Image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product ID")
    title: str = Field(..., description="Product title at time of order")
    price: float = Field(..., ge=0, description="Unit price at time of order")
    quantity: int = Field(..., ge=1, description="Quantity ordered")

class Order(BaseModel):
    user_email: str = Field(..., description="Email of the customer")
    shipping_address: str = Field(..., description="Shipping address")
    payment_method: str = Field(..., description="online | cod")
    status: str = Field("pending", description="Order status")
    items: List[OrderItem] = Field(..., description="List of ordered items")
    total: float = Field(..., ge=0, description="Order total amount")

class Wishlist(BaseModel):
    user_email: str = Field(..., description="Email of the user")
    product_id: str = Field(..., description="Product id marked as wishlist")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!

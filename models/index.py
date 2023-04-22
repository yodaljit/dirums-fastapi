from typing import Optional, Union
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

class Category(BaseModel):
    name: str
    slug: Optional[str]

class SubCategory(BaseModel):
    category: Category
    name: str
    slug: Optional[str]

class Medium(BaseModel):
    category: Category
    name: str
    slug: Optional[str]

class Space(BaseModel):
    name: str
    slug: str

class Subject(BaseModel):
    name: str
    slug: str

class SubSubject(BaseModel):
    subject: Subject
    name: str
    slug: str

class Variation(BaseModel):
    name: str
    options: List[str]

class Stock(BaseModel):
    available: bool
    quantity: int
    location: Optional[str]

class ProductStatus(BaseModel):
    active: bool
    approved: bool
    archived: bool

class Address(BaseModel):
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    zipcode: Optional[str]

class Vendor(BaseModel):
    name: str
    email: str
    is_individual: bool
    business_name: Optional[str]
    tax_id: Optional[str]
    website: Optional[str]
    phone_number: Optional[str]
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    zipcode: Optional[str]

class ProductImage(BaseModel):
    product_id: str
    url: str

class Sale(BaseModel):
    name: str
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    discount: float
    
class Product(BaseModel):
    name: str
    description: Optional[str]
    price: float
    sale_price: Optional[float]
    sale: Optional[Sale]
    variations: Optional[List[Variation]]
    length: Optional[str]
    height: Optional[str]
    width: Optional[str]
    measurement: Optional[str]
    weight: Optional[float]
    orientation: Optional[str]
    medium: Optional[Medium]
    category: Optional[Category]
    subcategory: Optional[List[SubCategory]]
    space: Optional[List[Space]]
    subject: Optional[List[Subject]]
    subsubject: Optional[List[SubSubject]]
    status: Optional[ProductStatus]
    vendor_id: str
    stock: Optional[Stock]
    slug: str
    images: Optional[List[ProductImage]]

class CartItem(BaseModel):
    product: Product
    quantity: int

class Cart(BaseModel):
    items: List[CartItem]

class Wishlist(BaseModel):
    items: List[Product]
    user_email: str

class VendorLogin(BaseModel):
    username: str
    otp: int

class OTP(BaseModel):
    code: str
    issued_to: str
    expiry_time: str
    expired: Optional[bool]

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: Optional[str] = None
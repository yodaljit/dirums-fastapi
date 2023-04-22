import json
from typing import Annotated, List
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Request, status, UploadFile
from fastapi.exceptions import HTTPException
from controllers.otp import get_otp, verify_otp
from jwttoken import create_access_token
from schemas.index import serializerList, SerailizerDict
from config.index import conn
from models.index import Product, Vendor, VendorLogin, Category, SubCategory, Medium, ProductImage
from bson import ObjectId, json_util
from oauth import oauth2_scheme
import pymongo
from uuid import uuid4
products = APIRouter()

# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
# @products.post('/login')
# def login(user: VendorLogin):
#     if user.username != "8092237808":
#         raise HTTPException(status_code=401,detail="Bad username or otp")

#     # subject identifier for who this token is for example id or username from database
#     access_token = Authorize.create_access_token(subject=user.username)
#     return {"access_token": access_token}
@products.get('/')
def get_products():
    return serializerList(conn.dirums.product.find())

@products.get('/vendors/{id}/products')
def all_products(id):
    vendor = SerailizerDict(conn.dirums.vendor.find_one({"_id": ObjectId(id)}))
    print(serializerList(conn.dirums.product.find({"vendor_id": id})))
    return serializerList(conn.dirums.product.find({"vendor_id": id}).sort('_id', pymongo.DESCENDING))

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, Category):
            return obj.dict()
        else:
            return super().default(obj)
        
@products.post('/vendors/{id}/add-product')
def add_product(id, product: Product):
    product_data = jsonable_encoder(product, custom_encoder={ObjectId: str, Category: lambda c: c.dict()})
    prod = conn.dirums.product.insert_one(dict(product_data))
    return serializerList(conn.dirums.product.find({"_id": ObjectId(prod.inserted_id)}))

@products.post('/vendors/{id}/upload-file/{product_id}')
def upload_file(id, product_id, request: Request, files: List[UploadFile] | None = None):
    vendor = SerailizerDict(conn.dirums.vendor.find_one({"_id": ObjectId(id)}))
    images = []
    for file in files:
        file_location = f"static/{uuid4()}-{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
            pimg = conn.dirums.product_image.insert_one({'product_id': product_id, 'url': str(request.url_for('static', path=file.filename))})
            images.append(serializerList(conn.dirums.product_image.find({'_id': ObjectId(pimg.inserted_id)}))[0])
            print(serializerList(conn.dirums.product_image.find({'_id': ObjectId(pimg.inserted_id)})))
            print(images)
    conn.dirums.product.find_one_and_update({"_id": ObjectId(product_id)}, {'$set': {'images': images}})
    return serializerList(conn.dirums.product.find({"vendor": vendor}))

@products.get('/vendors/{id}/get-artist-user')
def get_vendor(id):
    return {"artist": SerailizerDict(conn.dirums.vendor.find_one({"_id": ObjectId(id)}))}

# @products.post('/vendors/create-product')
# def create_products(product: Product):
#     conn.dirums.product.insert_one(dict(product))
#     return serializerList(conn.dirums.product.find())

@products.get('/vendors/get-categories')
def vendor_get_categories():
    return serializerList(conn.dirums.category.find())

@products.get('/vendors/{id}/address')
def vendor_get_address(id):
    return serializerList(conn.dirums.vendor.find({"_id": ObjectId(id)}))

@products.get('/vendors/{category}/fetch-subcategories')
async def vendor_get_subcategories(category):
    subcategories = conn.dirums.subcategory.find({"category._id": category})
    medium = conn.dirums.medium.find({"category._id": category})
    return {"subcategories": serializerList(subcategories), "medium": serializerList(medium)}


@products.post('/admin/create-category')
def create_category(category: Category):
    conn.dirums.category.insert_one(dict(category))
    return serializerList(conn.dirums.category.find())

@products.post('/admin/create-subcategory')
def create_subcategory(subcategory: SubCategory):
    cat = conn.dirums.category.find_one({"_id": ObjectId('643c295d6b449c361d1e196c')})
    conn.dirums.subcategory.insert_one(dict({"name":subcategory.name, "slug": subcategory.slug, "category": cat}))
    return serializerList(conn.dirums.category.find())


@products.post('/admin/create-medium')
def create_medium(medium: Medium):
    cat = conn.dirums.category.find_one({"_id": ObjectId('643c295d6b449c361d1e196c')})
    conn.dirums.medium.insert_one(dict({"name":medium.name, "slug": medium.slug, "category": cat}))
    return serializerList(conn.dirums.medium.find())

@products.get('/admin/get-categories')
def get_categories():
    return serializerList(conn.dirums.category.find())

@products.put('/admin/update-category')
def update_categories():
    cat = serializerList(conn.dirums.category.find())
    print(len(cat))
    for i in range(len(cat)):
        conn.dirums.category.find_one_and_update({'_id': ObjectId(cat[i]['_id'])}, {"$set": {'slug': slug[i]}})
    return serializerList(conn.dirums.category.find())

@products.post('/create-vendor')
def create_vendor(vendor: Vendor):
    conn.dirums.vendor.insert_one({"name": vendor.name, "email": vendor.email, "phone_number": vendor.phone_number, 'is_individual': vendor.is_individual, "tax_id": vendor.tax_id, "website": vendor.website, "business_name": vendor.business_name, "street": vendor.street, "city": vendor.city, "state": vendor.state, "country": vendor.country, "zipcode": vendor.zipcode})
    return serializerList(conn.dirums.vendor.find())

@products.post('/vendors/{id}/address/get-otp')
def getOTP(phone):
    user = conn.dirums.vendor.find_one({"phone_number": phone})
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return get_otp(user)

@products.post('/vendors/{id}/address/verify-otp')
def verifyOTP(phone, otp):
    user = conn.dirums.vendor.find_one({"phone_number": phone})
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    isValid = verify_otp(otp, user)

    if isValid[0]:
        return isValid[1]
    else:
        return isValid
    
@products.post('/vendors/{id}/update-address')
def update_address(id, vendor: Vendor):
    conn.dirums.vendor.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(vendor)})
    return serializerList(conn.dirums.vendor.find({"_id": ObjectId(id)}))
from fastapi import FastAPI

app = FastAPI()

# Product database
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 6999, "category": "Electronics", "in_stock": False},

    # Q1 → Added products
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]


# Q1
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


# Q2
@app.get("/products/category/{category_name}")
def category_filter(category_name: str):
    result = [p for p in products if p["category"].lower() == category_name.lower()]

    if not result:
        return {"error": "No products found in this category"}

    return {"category": category_name, "products": result, "total": len(result)}


# Q3
@app.get("/products/instock")
def instock_products():
    available = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": available,
        "count": len(available)
    }


# Q4
@app.get("/store/summary")
def store_summary():
    instock = len([p for p in products if p["in_stock"]])
    outstock = len(products) - instock

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }


# Q5
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matches = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not matches:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": matches,
        "total_matches": len(matches)
    }


# ⭐ BONUS
@app.get("/products/deals")
def best_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
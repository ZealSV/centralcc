from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)
    
    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    sql_to_execute = """
        INSERT INTO carts (customer_name)
        VALUES (:customer_name)
        RETURNING cart_id
    """
    params = {"customer_name": new_cart.customer_name}
    with db.engine.begin() as connection:
        id = connection.execute(sqlalchemy.text(sql_to_execute), params).scalar_one()

    return {'cart_id': id}

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    
    sql_to_execute = """
        INSERT INTO cart_items (cart_id, quantity, potion_id) 
        SELECT :cart_id, :quantity, potions.id 
        FROM potions WHERE potions.sku = :item_sku
    """
    params = {"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku}

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute), params)
    return "OK"


class CartCheckout(BaseModel):
    payment: str
    potions_bought: dict

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """Process checkout."""
    sql1 = """
        SELECT SUM(quantity) AS tot_potions
        FROM cart_items
        WHERE cart_id = :cart_id
    """
    sql2 = """
        SELECT SUM(quantity*price) AS tot_gold
        FROM cart_items
        JOIN potions ON potions.id = cart_items.potion_id
        WHERE cart_id = :cart_id
    """
    sql3 = """
        INSERT INTO total_potions (potion_change, potion_id)
        SELECT (cart_items.quantity * -1), cart_items.potion_id
        FROM cart_items
        WHERE cart_items.cart_id = :cart_id
    """
    sql4 = """
        INSERT INTO total_gold (gold_change) 
        VALUES (:gold_paid)
    """
    cartparam = {"cart_id": cart_id}
    goldparam = {"gold_paid": tot_gold}
    
    with db.engine.begin() as connection:
        tot_potions = connection.execute(sqlalchemy.text(sql1), cartparam).scalar_one()
        tot_gold = connection.execute(sqlalchemy.text(sql2), cartparam).scalar_one()
        connection.execute(sqlalchemy.text(sql3), cartparam)
        connection.execute(sqlalchemy.text(sql4), goldparam)

    return {"total_potions_bought": tot_potions, "total_gold_paid": tot_gold}

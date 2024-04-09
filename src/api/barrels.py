from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int



@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")
    total_ml = sum(barrel.ml_per_barrel for barrel in barrels_delivered)
    sql_to_execute = f"UPDATE global_inventory SET num_green_ml + {total_ml}"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    sql_to_execute = "SELECT num_green_potions FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        value = result.scalar_one()
    if value < 10:
        value += 1
    
    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": value,
        }
    ]


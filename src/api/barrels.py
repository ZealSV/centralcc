from fastapi import APIRouter, Depends, HTTPException
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
    sql_to_execute = f"UPDATE global_inventory SET num_green_ml = num_green_ml + :total_ml", {"total_ml": total_ml}
    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql_to_execute))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update inventory")
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """

    if not wholesale_catalog:
        return []

    print(wholesale_catalog)

    sql_to_execute = "SELECT num_green_potions, num_blue_potions, num_red_potions FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        num_green_potions, num_blue_potions, num_red_potions = result.scalar_one()

    if num_green_potions < 10:
        num_green_potions += 1
    elif num_blue_potions >= 10 and num_blue_potions < 20:
        num_blue_potions += 1
    elif num_red_potions >= 20:
        num_red_potions += 1

    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": num_green_potions,
        },
        {
            "sku": "SMALL_BLUE_BARREL",
            "quantity": num_blue_potions,
        },
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": num_red_potions,
        }
    ]


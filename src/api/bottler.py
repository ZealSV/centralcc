from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")
    total_ml_delivered = sum(potion.quantity for potion in potions_delivered)
    total_ml_leftover = total_ml_delivered % 100 #figure out how to update
    sql_to_execute = f"UPDATE global_inventory SET num_green_ml = num_green_ml % 100 - {total_ml_leftover}"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_execute))
    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    sql_to_execute = "SELECT num_green_ml FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        value = result.scalar_one()
    mixed_potions_amount = value // 100
    
    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": mixed_potions_amount,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
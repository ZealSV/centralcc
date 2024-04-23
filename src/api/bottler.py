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

    sql_to_execute_1 = """INSERT INTO total_potions (potion_amt, potion_id) SELECT :potion_amt, potions.id FROM potions WHERE potions.potion_type = :potion_type""", [{"potion_amt": potion.quantity, "potion_type": potion.potion_type}]
    sql_to_execute_2 = """INSERT INTO total_mls (red_ml_amt, green_ml_amt, blue_ml_amt, dark_ml_amt) VALUES (:red_ml, :green_ml, :blue_ml, :dark_ml)""", [{"red_ml": - red_ml, "blue_ml": - blue_ml, "green_ml": - green_ml,"dark_ml": - dark_ml}]

    with db.engine.begin() as connection:
        red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        dark_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)
        total_potions = sum(potion.quantity for potion in potions_delivered)

        for potion in potions_delivered:
            connection.execute(sqlalchemy.text(sql_to_execute_1))
            connection.execute(sqlalchemy.text(sql_to_execute_2))

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    
    sql_to_execute_1 = """SELECT SUM(red_ml_amt) AS red_ml, SUM(green_ml_amt) AS green_ml, SUM(blue_ml_amt) AS blue_ml, SUM(dark_ml_amt) AS dark_ml FROM total_mls"""
    sql_to_execute_2 = """SELECT COALESCE(SUM(potion_amt), 0) AS total_inventory FROM total_potions"""
    sql_to_execute_3 = """SELECT p.id, p.potion_type, p.sku, COALESCE(SUM(pl.potion_amt), 0) AS inventory FROM potions p JOIN total_potions pl ON p.id = pl.potion_id GROUP BY p.id"""

    with db.engine.begin() as connection:
        total_mls = connection.execute(sqlalchemy.text(sql_to_execute_1)).first()
        total_inventory = connection.execute(sqlalchemy.text(sql_to_execute_2)).scalar_one()
        potions = connection.execute(sqlalchemy.text(sql_to_execute_3)).fetchall()

    plan = []
    quantity = {}
    max_inventory = 10000
    max_quantity_per_potion = 5

    for potion in potions:
        quantity[potion.sku] = 0

    while total_inventory < max_inventory:
        for potion in potions:
            if total_inventory < max_inventory and potion.inventory < max_quantity_per_potion \
                    and sum(potion.potion_type) <= total_mls.red_ml and sum(potion.potion_type[1:]) <= total_mls.green_ml \
                    and sum(potion.potion_type[2:]) <= total_mls.blue_ml and potion.inventory < max_quantity_per_potion:
                for i in range(len(potion.potion_type)):
                    total_mls[i] -= potion.potion_type[i]
                quantity[potion.sku] += 1
                potion.inventory += 1
                total_inventory += 1

    for potion in potions:
        if quantity[potion.sku] != 0:
            plan.append({
                "potion_type": potion.potion_type,
                "quantity": quantity[potion.sku]
            })

    return plan


if __name__ == "__main__":
    print(get_bottle_plan())
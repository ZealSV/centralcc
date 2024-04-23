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

    gold_spent = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0
    dark_ml = 0
    for barrel in barrels_delivered:
        gold_spent += barrel.price * barrel.quantity
        if(barrel.potion_type == [1,0,0,0]):
            red_ml += barrel.ml_per_barrel * barrel.quantity
        elif(barrel.potion_type == [0,1,0,0]):
            green_ml += barrel.ml_per_barrel * barrel.quantity
        elif(barrel.potion_type == [0,0,1,0]):
            blue_ml += barrel.ml_per_barrel * barrel.quantity
        elif(barrel.potion_type == [0,0,0,1]):
            dark_ml += barrel.ml_per_barrel * barrel.quantity
        else:
            raise Exception('Invalid potion type')

    print(f"total gold spent: {gold_spent} red_ml: {red_ml} blue_ml: {blue_ml} green_ml: {green_ml} dark_ml: {dark_ml}")

    sql_to_execute_1 = """INSERT INTO total_gold (gold_amt) VALUES (:gold_spent) """, [{"gold_spent": - gold_spent}]
    sql_to_execute_2 = """INSERT INTO total_mls (red_ml_amt, green_ml_amt, blue_ml_amt, dark_ml_amt) VALUES (:red_ml, :green_ml, :blue_ml, :dark_ml) """, [{"red_ml": red_ml, "green_ml": green_ml,"blue_ml": blue_ml,"dark_ml": dark_ml}]

    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql_to_execute_1))
            connection.execute(sqlalchemy.text(sql_to_execute_2))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update inventory")
    return "OK"

@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    
    sql_gold = """SELECT SUM(gold_amt) FROM total_gold"""
    # sql_potion = """SELECT SUM(potion_amt) FROM total_potions"""
    with db.engine.begin() as connection:
        total_gold = connection.execute(sqlalchemy.text(sql_gold)).scalar_one() or 0
        # total_potion = connection.execute(sqlalchemy.text(sql_potion)).scalar_one() or 0

    current_gold = total_gold
    plan = []
    purchased_quantities = {}

    sorted_catalog = sorted(wholesale_catalog, key=lambda x: x.price)

    for barrel in sorted_catalog:
        if current_gold < barrel.price or barrel.quantity <= 0:
            continue

        max_quantity = min(current_gold // barrel.price, barrel.quantity)

        purchased_quantities[barrel.sku] = max_quantity
        current_gold -= max_quantity * barrel.price

    for sku, quantity in purchased_quantities.items():
        if quantity > 0:
            plan.append({"sku": sku, "quantity": quantity})

    return plan

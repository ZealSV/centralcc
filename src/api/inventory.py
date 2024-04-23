from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    sql_gold = """SELECT SUM(gold_amt) AS total_gold FROM total_gold """
    sql_red = """SELECT SUM(red_ml_amt) AS red_amt FROM total_mls """
    sql_blue = """SELECT SUM(green_ml_amt) AS green_amt FROM total_mls """
    sql_green = """SELECT SUM(blue_ml_amt) AS blue_amt  FROM total_mls """
    sql_dark = """SELECT SUM(dark_ml_amt) AS dark_amt FROM total_mls"""
    sql_potions = """SELECT SUM(potion_amt) AS inventory FROM total_potions"""

    with db.engine.begin() as connection:
        total_gold = connection.execute(sqlalchemy.text(sql_gold)).scalar_one()
        red_amt = connection.execute(sqlalchemy.text(sql_red)).scalar_one()
        blue_amt = connection.execute(sqlalchemy.text(sql_blue)).scalar_one()
        green_amt = connection.execute(sqlalchemy.text(sql_green)).scalar_one()
        dark_amt = connection.execute(sqlalchemy.text(sql_dark)).scalar_one()
        total_potions = connection.execute(sqlalchemy.text(sql_potions)).scalar_one()

    total_mls = red_amt + green_amt + blue_amt + dark_amt

    return {"number_of_potions": total_potions, "ml_in_barrels": total_mls, "gold": total_gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 50,
        "ml_capacity": 10000
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"

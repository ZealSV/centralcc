from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = "SELECT num_red_potions, num_blue_potions, num_green_potions FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        red_potions, blue_potions, green_potions = result.scalar_one()
    return [
        {
            "sku": "RED_POTION_0",
            "name": "red potion",
            "quantity": red_potions,
            "price": 55,
            "potion_type": [100, 0, 0, 0],
        },
        {
            "sku": "BLUE_POTION_0",
            "name": "blue potion",
            "quantity": blue_potions,
            "price": 70,
            "potion_type": [0, 0, 100, 0],
        },
        {
            "sku": "GREEN_POTION_0",
            "name": "green potion",
            "quantity": green_potions,
            "price": 50,
            "potion_type": [0, 100, 0, 0],
        }
        ]

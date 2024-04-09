from fastapi import APIRouter
import sqlalchemy
from src import database as db
from src.api.bottler import mixed_potions_amount

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = "SELECT num_green_potions FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
        value = result.scalar_one()
    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": value,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }
        ]

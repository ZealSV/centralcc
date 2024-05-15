from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_execute = """SELECT sku, SUM(total_potions.potion_change) AS inventory, price, potion_type FROM potions JOIN total_potions ON total_potions.potion_id = potions.id GROUP BY potions.id"""
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute))
    catalog = []
    for row in result:
        if row.inventory > 0:
            catalog.append({
                "sku": row.sku,
                "name": row.sku,
                "quantity": row.inventory,
                "price": row.price,
                "potion_type": row.potion_type,
            })

    return catalog

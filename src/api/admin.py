from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

class ResetResponse(BaseModel):
    message: str = "OK"

@router.post("/reset", response_model=ResetResponse)
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_state SET gold = 100"))

        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = 0, num_blue_potions = 0, num_green_potions = 0"))

        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("DELETE FROM barrels"))

        return ResetResponse()
    except Exception as e:
        return ResetResponse(message="Failed to reset: " + str(e))
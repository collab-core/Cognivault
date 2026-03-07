from fastapi import HTTPException
from pydantic import BaseModel


def non_null_update_data(payload: BaseModel) -> dict:
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")
    return update_data

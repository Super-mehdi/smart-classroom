from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/")
async def read_example():
    return {"message": "This is an example endpoint"}
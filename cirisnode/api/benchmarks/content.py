from fastapi import APIRouter
from cirisnode.utils.cache import get_cached_he300_data, get_cached_simplebench_data

router = APIRouter(tags=["benchmarks_content"])

@router.get("/he300", response_model=list)
def get_he300_content():
    """
    Endpoint to retrieve the content of HE-300 scenarios.
    """
    return get_cached_he300_data()

@router.get("/simplebench", response_model=list)
def get_simplebench_content():
    """
    Endpoint to retrieve the content of SimpleBench scenarios.
    """
    return get_cached_simplebench_data()

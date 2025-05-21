from functools import lru_cache
from cirisnode.utils.data_loaders import load_he300_data, load_simplebench_data # Updated import

@lru_cache(maxsize=1)
def get_cached_he300_data():
    """Retrieve cached HE-300 data."""
    return load_he300_data()

@lru_cache(maxsize=1)
def get_cached_simplebench_data():
    """Retrieve cached SimpleBench data."""
    return load_simplebench_data()

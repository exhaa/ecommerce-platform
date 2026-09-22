from app.redis_client import redis_client


PRODUCT_CACHE_KEY = "catalog:products"


def invalidate_product_cache():
    redis_client.delete(PRODUCT_CACHE_KEY)
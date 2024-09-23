import redis

class Redis:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Redis, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, 'r'):
            self.r = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True)

    def store_value(self, key: str, value: str):
        self.r.set(key, value)

    def get_value(self, key: str):
        return self.r.get(key)

    def delete_value(self, key: str):
        self.r.delete(key)

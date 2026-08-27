import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.set("test_key", "hello from python")
value = r.get("test_key")
print(value)
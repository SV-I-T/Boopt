from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "FileSystemCache", "CACHE_DIR": "cache"})
cache_simple = Cache(config={"CACHE_TYPE": "SimpleCache"})

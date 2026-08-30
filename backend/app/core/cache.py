"""
Redis Cache Service — Fast In-Memory Caching for TOP WorX ERP
============================================================

Provides:
  - Redis-backed cache with TTL and serialization
  - Decorator-based caching for endpoint functions
  - Pattern-based cache invalidation
  - Fallback to in-memory cache if Redis unavailable
  - Cache stats monitoring

Usage:
    from app.core.cache import cache, cached, invalidate_pattern

    # Decorator-based caching
    @cached(ttl=300, key_prefix="dashboard")
    async def get_dashboard_stats(db):
        ...

    # Manual caching
    await cache.set("user:123:permissions", perms, ttl=600)
    perms = await cache.get("user:123:permissions")

    # Pattern invalidation
    await invalidate_pattern("dashboard:*")
"""
from __future__ import annotations

import asyncio
import json
import logging
import hashlib
import functools
import inspect
from typing import Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# IN-MEMORY FALLBACK CACHE (used when Redis unavailable)
# ═════════════════════════════════════════════════════════════════════════════

class InMemoryCache:
    """Simple in-memory cache with TTL — fallback when Redis is down."""

    def __init__(self, max_size: int = 1000):
        self._store: dict[str, tuple[Any, float]] = {}
        self._max_size = max_size

    async def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expires_at = self._store[key]
            if expires_at > asyncio.get_event_loop().time():
                return value
            del self._store[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        if len(self._store) >= self._max_size:
            self._evict()
        expires_at = asyncio.get_event_loop().time() + ttl
        self._store[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def clear(self) -> None:
        self._store.clear()

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern (e.g., 'dashboard:*')."""
        import fnmatch
        keys_to_delete = [
            k for k in self._store.keys()
            if fnmatch.fnmatch(k, pattern)
        ]
        for k in keys_to_delete:
            del self._store[k]
        return len(keys_to_delete)

    async def get_stats(self) -> dict:
        now = asyncio.get_event_loop().time()
        alive = sum(1 for _, (_, exp) in self._store.items() if exp > now)
        return {
            "backend": "in-memory",
            "total_keys": len(self._store),
            "alive_keys": alive,
        }

    def _evict(self):
        """Remove expired entries, then oldest 10% if still over limit."""
        now = asyncio.get_event_loop().time()
        expired = [k for k, (_, exp) in self._store.items() if exp <= now]
        for k in expired:
            del self._store[k]
        if len(self._store) >= self._max_size:
            sorted_keys = sorted(
                self._store.keys(),
                key=lambda k: self._store[k][1]  # sort by expiry
            )
            remove_count = max(1, self._max_size // 10)
            for k in sorted_keys[:remove_count]:
                del self._store[k]


# ═════════════════════════════════════════════════════════════════════════════
# REDIS CACHE (production)
# ═════════════════════════════════════════════════════════════════════════════

class RedisCache:
    """Redis-backed async cache with JSON serialization and TTL."""

    def __init__(self):
        self._redis = None
        self._connected = False
        self._prefix = "topworx:"

    async def connect(self, redis_url: str) -> None:
        """Connect to Redis. Falls back to in-memory if unavailable."""
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            await self._redis.ping()
            self._connected = True
            logger.info(f"Redis cache connected: {redis_url.split('@')[-1]}")
        except Exception as e:
            logger.warning(f"Redis unavailable ({e}), using in-memory cache")
            self._connected = False

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()
            self._connected = False

    def _key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        if not self._connected:
            return await _memory_cache.get(key)
        try:
            raw = await self._redis.get(self._key(key))
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Cache GET error: {e}")
            return await _memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        if not self._connected:
            return await _memory_cache.set(key, value, ttl)
        try:
            serialized = json.dumps(value, default=str)
            await self._redis.setex(self._key(key), ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache SET error: {e}")
            await _memory_cache.set(key, value, ttl)

    async def delete(self, key: str) -> None:
        if not self._connected:
            return await _memory_cache.delete(key)
        try:
            await self._redis.delete(self._key(key))
        except Exception as e:
            logger.warning(f"Cache DELETE error: {e}")
            await _memory_cache.delete(key)

    async def clear(self) -> None:
        if not self._connected:
            return await _memory_cache.clear()
        try:
            keys = await self._redis.keys(f"{self._prefix}*")
            if keys:
                await self._redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache CLEAR error: {e}")
            await _memory_cache.clear()

    async def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not self._connected:
            return await _memory_cache.invalidate_pattern(pattern)
        try:
            full_pattern = self._key(pattern)
            keys = await self._redis.keys(full_pattern)
            if keys:
                await self._redis.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache INVALIDATE error: {e}")
            return await _memory_cache.invalidate_pattern(pattern)

    async def get_stats(self) -> dict:
        if not self._connected:
            return await _memory_cache.get_stats()
        try:
            info = await self._redis.info("stats")
            memory = await self._redis.info("memory")
            keys = await self._redis.dbsize()
            return {
                "backend": "redis",
                "connected": True,
                "total_keys": keys,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    round(info.get("keyspace_hits", 0) / max(
                        info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
                    ) * 100, 1)
                ),
                "used_memory": memory.get("used_memory_human", "unknown"),
            }
        except Exception as e:
            return {"backend": "redis", "connected": False, "error": str(e)}


# ═════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCES
# ═════════════════════════════════════════════════════════════════════════════

_memory_cache = InMemoryCache()
cache = RedisCache()


# ═════════════════════════════════════════════════════════════════════════════
# CACHE KEY HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def make_cache_key(*parts: Any) -> str:
    """Build a colon-separated cache key from parts."""
    return ":".join(str(p) for p in parts)


def hash_args(*args, **kwargs) -> str:
    """Hash function arguments for cache key generation."""
    raw = json.dumps({"args": args, "kwargs": kwargs}, default=str)
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ═════════════════════════════════════════════════════════════════════════════
# CACHE DECORATORS
# ═════════════════════════════════════════════════════════════════════════════

def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None,
    cache_none: bool = False,
):
    """
    Decorator that caches async function results in Redis.

    Args:
        ttl: Time-to-live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key (e.g., "dashboard", "user")
        key_builder: Custom function to build cache key from args
        cache_none: Whether to cache None results

    Usage:
        @cached(ttl=300, key_prefix="dashboard")
        async def get_dashboard_stats(db):
            ...

        @cached(ttl=600, key_prefix="user", key_builder=lambda user_id, **kw: f"perms:{user_id}")
        async def get_user_permissions(user_id, db):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Skip 'db' and 'self' args for key generation
                key_parts = [
                    a for a in args
                    if not hasattr(a, 'execute') and not hasattr(a, 'session')
                ]
                filtered_kwargs = {
                    k: v for k, v in kwargs.items()
                    if k not in ('db', 'session', 'self', 'current_user')
                }
                args_hash = hash_args(*key_parts, **filtered_kwargs)
                cache_key = f"{key_prefix}:{args_hash}" if key_prefix else args_hash

            # Try cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            if result is None and not cache_none:
                # Cache miss — compute
                pass

            # Compute
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None or cache_none:
                await cache.set(cache_key, result, ttl=ttl)

            return result

        # Expose invalidation on the decorated function
        wrapper.invalidate = lambda: cache.invalidate_pattern(f"{key_prefix}:*")
        wrapper.cache_key_prefix = key_prefix
        return wrapper

    return decorator


def cache_invalidate(pattern: str):
    """
    Decorator that invalidates cache entries after function execution.

    Usage:
        @cache_invalidate("dashboard:*")
        async def update_setting(key, value, db):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache.invalidate_pattern(pattern)
            return result
        return wrapper
    return decorator


# ═════════════════════════════════════════════════════════════════════════════
# CONVENIENT INVALIDATION HELPERS
# ═════════════════════════════════════════════════════════════════════════════

async def invalidate_pattern(pattern: str) -> int:
    """Invalidate all cache entries matching a glob pattern."""
    return await cache.invalidate_pattern(pattern)


async def invalidate_user_cache(user_id: int) -> None:
    """Invalidate all cached data for a specific user."""
    await cache.invalidate_pattern(f"user:{user_id}:*")
    await cache.invalidate_pattern(f"permissions:{user_id}:*")


async def invalidate_dashboard_cache() -> None:
    """Invalidate all dashboard-related caches."""
    await cache.invalidate_pattern("dashboard:*")


async def invalidate_settings_cache() -> None:
    """Invalidate all system settings caches."""
    await cache.invalidate_pattern("settings:*")


# ═════════════════════════════════════════════════════════════════════════════
# CACHE WARMING (call on startup)
# ═════════════════════════════════════════════════════════════════════════════

async def warm_cache(db=None) -> None:
    """
    Pre-populate cache with frequently accessed data on startup.
    Call this from the lifespan handler.
    """
    if not cache._connected:
        return

    logger.info("Warming cache...")

    # Warm system settings
    try:
        from sqlalchemy import select
        from app.models.settings import SystemSetting
        result = await db.execute(select(SystemSetting))
        settings_list = result.scalars().all()
        for s in settings_list:
            await cache.set(
                f"settings:{s.key}",
                {"value": s.value, "value_type": s.value_type, "category": s.category.value},
                ttl=3600,
            )
        logger.info(f"  Warmed {len(settings_list)} system settings")
    except Exception as e:
        logger.warning(f"  Failed to warm settings cache: {e}")

    logger.info("Cache warming complete")

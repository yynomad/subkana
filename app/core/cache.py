"""
通用内存缓存模块

提供 TTL、容量限制、命中统计的线程安全内存缓存。
零外部依赖，适合单进程/单 worker 场景。
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar
from collections import OrderedDict

logger = logging.getLogger(__name__)

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _CacheEntry(Generic[V]):
    """缓存条目"""

    value: V
    expires_at: float  # time.monotonic 时间戳


@dataclass
class CacheStats:
    """缓存统计信息"""

    size: int = 0
    capacity: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryCache(Generic[K, V]):
    """
    内存缓存（支持 TTL、容量限制、LRU 淘汰）

    用法:
        cache = MemoryCache[str, dict](ttl=300, max_size=1000)
        cache.set("key", {"data": 1})
        data = cache.get("key")
        stats = cache.stats()
        cache.clear()
    """

    def __init__(self, ttl: float = 300, max_size: int = 1000, namespace: str = "default"):
        """
        Args:
            ttl: 缓存生存时间（秒），默认 5 分钟
            max_size: 最大缓存条目数，超出后淘汰最久未使用的条目
            namespace: 缓存命名空间，仅用于日志/统计标识
        """
        self.ttl = ttl
        self.max_size = max_size
        self.namespace = namespace
        self._store: OrderedDict[K, _CacheEntry[V]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    # ── 公共方法 ─────────────────────────────────────────────

    def get(self, key: K) -> Optional[V]:
        """
        获取缓存值。

        如果 key 不存在或已过期返回 None，否则返回缓存的值。
        每次成功获取会将条目移到末尾（LRU 策略）。
        """
        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            logger.debug("[%s] 缓存未命中: %s", self.namespace, key)
            return None

        # 检查是否过期
        if time.monotonic() > entry.expires_at:
            self._store.pop(key)
            self._misses += 1
            logger.debug("[%s] 缓存过期: %s", self.namespace, key)
            return None

        # 移到末尾（LRU）
        self._store.move_to_end(key)
        self._hits += 1
        logger.debug("[%s] 缓存命中: %s", self.namespace, key)
        return entry.value

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        """
        写入缓存。

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 可选的自定义 TTL（秒），默认使用实例的 ttl
        """
        effective_ttl = ttl if ttl is not None else self.ttl
        expires_at = time.monotonic() + effective_ttl

        # 已达最大容量，淘汰最久未使用的条目
        if len(self._store) >= self.max_size and key not in self._store:
            self._store.popitem(last=False)
            self._evictions += 1
            logger.debug("[%s] LRU 淘汰一个条目", self.namespace)

        self._store[key] = _CacheEntry(value=value, expires_at=expires_at)
        self._store.move_to_end(key)
        logger.debug("[%s] 缓存写入: %s (TTL=%ds)", self.namespace, key, effective_ttl)

    def delete(self, key: K) -> bool:
        """删除指定 key。存在且已删除返回 True，否则 False。"""
        if key in self._store:
            del self._store[key]
            logger.debug("[%s] 缓存删除: %s", self.namespace, key)
            return True
        return False

    def clear(self) -> None:
        """清空所有缓存条目（不重置统计）"""
        self._store.clear()
        logger.info("[%s] 缓存已清空", self.namespace)

    def has(self, key: K) -> bool:
        """检查 key 是否存在且未过期"""
        entry = self._store.get(key)
        if entry is None:
            return False
        if time.monotonic() > entry.expires_at:
            self._store.pop(key)
            return False
        return True

    # ── 统计 ─────────────────────────────────────────────────

    def stats(self) -> CacheStats:
        """获取缓存统计信息"""
        # 清理过期条目后再统计
        self._evict_expired()
        return CacheStats(
            size=len(self._store),
            capacity=self.max_size,
            hits=self._hits,
            misses=self._misses,
            evictions=self._evictions,
        )

    def reset_stats(self) -> None:
        """重置命中/未命中/淘汰计数"""
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    # ── 内部方法 ─────────────────────────────────────────────

    def _evict_expired(self) -> None:
        """移除所有过期条目"""
        now = time.monotonic()
        expired_keys = [k for k, v in self._store.items() if now > v.expires_at]
        for k in expired_keys:
            del self._store[k]
        if expired_keys:
            logger.debug("[%s] 清理了 %d 个过期条目", self.namespace, len(expired_keys))

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return (
            f"MemoryCache(namespace={self.namespace!r}, "
            f"size={len(self._store)}, max_size={self.max_size}, "
            f"ttl={self.ttl}s, hits={self._hits}, misses={self._misses})"
        )

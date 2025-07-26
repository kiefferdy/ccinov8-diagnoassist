"""
Performance Optimization System for DiagnoAssist Backend

This module provides performance optimization features including caching,
connection pooling, query optimization, and async processing improvements.
"""
import asyncio
import time
import json
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union, TypeVar, Generic
from dataclasses import dataclass
from functools import wraps
import threading
import logging

from app.core.monitoring import monitoring

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheStrategy(str):
    """Cache strategies"""
    LRU = "lru"
    TTL = "ttl"
    LFU = "lfu"


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)


class MemoryCache:
    """In-memory cache with multiple eviction strategies"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        def cleanup_expired():
            while True:
                try:
                    self._cleanup_expired_entries()
                    time.sleep(60)  # Clean up every minute
                except Exception as e:
                    logger.error(f"Error in cache cleanup: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                monitoring.metrics.increment_counter("cache_misses", labels={"cache": "memory"})
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired:
                del self._cache[key]
                monitoring.metrics.increment_counter("cache_misses", labels={"cache": "memory"})
                return None
            
            # Update access metadata
            entry.last_accessed = datetime.utcnow()
            entry.access_count += 1
            
            monitoring.metrics.increment_counter("cache_hits", labels={"cache": "memory"})
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        with self._lock:
            # Use default TTL if not specified
            ttl = ttl or self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=1,
                ttl_seconds=ttl
            )
            
            # Add to cache
            self._cache[key] = entry
            
            # Evict if over capacity
            if len(self._cache) > self.max_size:
                self._evict_entries()
            
            monitoring.metrics.increment_counter("cache_sets", labels={"cache": "memory"})
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def _evict_entries(self):
        """Evict entries using LRU strategy"""
        # Remove 10% of entries (LRU)
        entries_to_remove = max(1, len(self._cache) // 10)
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        for i in range(entries_to_remove):
            key, _ = sorted_entries[i]
            del self._cache[key]
    
    def _cleanup_expired_entries(self):
        """Remove expired entries"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            
            if total_entries == 0:
                return {
                    "total_entries": 0,
                    "max_size": self.max_size,
                    "usage_percent": 0
                }
            
            now = datetime.utcnow()
            expired_count = sum(1 for entry in self._cache.values() if entry.is_expired)
            
            access_counts = [entry.access_count for entry in self._cache.values()]
            avg_access_count = sum(access_counts) / len(access_counts) if access_counts else 0
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_count,
                "max_size": self.max_size,
                "usage_percent": (total_entries / self.max_size) * 100,
                "average_access_count": avg_access_count
            }


class ConnectionPool:
    """Generic connection pool for database connections"""
    
    def __init__(
        self, 
        connection_factory: Callable,
        min_connections: int = 5,
        max_connections: int = 20,
        max_idle_time: int = 300  # 5 minutes
    ):
        self.connection_factory = connection_factory
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        
        self._pool: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._created_connections = 0
        
    async def get_connection(self):
        """Get connection from pool"""
        async with self._lock:
            # Try to get idle connection
            now = datetime.utcnow()
            
            for i, conn_info in enumerate(self._pool):
                if not conn_info["in_use"]:
                    # Check if connection is still valid and not too old
                    idle_time = (now - conn_info["last_used"]).total_seconds()
                    
                    if idle_time < self.max_idle_time:
                        conn_info["in_use"] = True
                        conn_info["last_used"] = now
                        monitoring.metrics.increment_counter("connection_pool_hits")
                        return conn_info["connection"]
                    else:
                        # Remove expired connection
                        self._pool.pop(i)
                        self._created_connections -= 1
            
            # Create new connection if under limit
            if self._created_connections < self.max_connections:
                try:
                    connection = await self.connection_factory()
                    conn_info = {
                        "connection": connection,
                        "created_at": now,
                        "last_used": now,
                        "in_use": True
                    }
                    self._pool.append(conn_info)
                    self._created_connections += 1
                    
                    monitoring.metrics.increment_counter("connection_pool_creates")
                    return connection
                    
                except Exception as e:
                    logger.error(f"Failed to create new connection: {e}")
                    raise
            
            # Pool is full, wait for connection to become available
            monitoring.metrics.increment_counter("connection_pool_waits")
            raise Exception("Connection pool exhausted")
    
    async def return_connection(self, connection):
        """Return connection to pool"""
        async with self._lock:
            for conn_info in self._pool:
                if conn_info["connection"] is connection:
                    conn_info["in_use"] = False
                    conn_info["last_used"] = datetime.utcnow()
                    monitoring.metrics.increment_counter("connection_pool_returns")
                    return
    
    async def close_all_connections(self):
        """Close all connections in pool"""
        async with self._lock:
            for conn_info in self._pool:
                try:
                    if hasattr(conn_info["connection"], "close"):
                        await conn_info["connection"].close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self._pool.clear()
            self._created_connections = 0
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            total_connections = len(self._pool)
            in_use_connections = sum(1 for conn in self._pool if conn["in_use"])
            idle_connections = total_connections - in_use_connections
            
            return {
                "total_connections": total_connections,
                "in_use_connections": in_use_connections,
                "idle_connections": idle_connections,
                "max_connections": self.max_connections,
                "min_connections": self.min_connections,
                "utilization_percent": (in_use_connections / self.max_connections) * 100 if self.max_connections > 0 else 0
            }


class QueryOptimizer:
    """Database query optimization utilities"""
    
    def __init__(self):
        self.query_cache = MemoryCache(max_size=500, default_ttl=300)  # 5 minute TTL
        self.query_stats = {}
        self._lock = threading.Lock()
    
    def cache_query_result(self, query: str, params: Dict[str, Any], result: Any, ttl: Optional[int] = None):
        """Cache query result"""
        cache_key = self._generate_cache_key(query, params)
        self.query_cache.set(cache_key, result, ttl)
    
    def get_cached_result(self, query: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached query result"""
        cache_key = self._generate_cache_key(query, params)
        return self.query_cache.get(cache_key)
    
    def _generate_cache_key(self, query: str, params: Dict[str, Any]) -> str:
        """Generate cache key for query and parameters"""
        # Create consistent key from query and parameters
        params_str = json.dumps(params, sort_keys=True)
        key_string = f"{query}:{params_str}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def record_query_stats(self, query: str, execution_time_ms: float, result_count: int):
        """Record query execution statistics"""
        with self._lock:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            
            if query_hash not in self.query_stats:
                self.query_stats[query_hash] = {
                    "query_sample": query[:100] + "..." if len(query) > 100 else query,
                    "execution_count": 0,
                    "total_time_ms": 0,
                    "min_time_ms": float('inf'),
                    "max_time_ms": 0,
                    "total_results": 0
                }
            
            stats = self.query_stats[query_hash]
            stats["execution_count"] += 1
            stats["total_time_ms"] += execution_time_ms
            stats["min_time_ms"] = min(stats["min_time_ms"], execution_time_ms)
            stats["max_time_ms"] = max(stats["max_time_ms"], execution_time_ms)
            stats["total_results"] += result_count
    
    def get_slow_queries(self, threshold_ms: float = 1000) -> List[Dict[str, Any]]:
        """Get queries that exceed execution time threshold"""
        with self._lock:
            slow_queries = []
            
            for query_hash, stats in self.query_stats.items():
                avg_time = stats["total_time_ms"] / stats["execution_count"]
                
                if avg_time > threshold_ms or stats["max_time_ms"] > threshold_ms:
                    slow_queries.append({
                        "query_hash": query_hash,
                        "query_sample": stats["query_sample"],
                        "avg_time_ms": avg_time,
                        "max_time_ms": stats["max_time_ms"],
                        "execution_count": stats["execution_count"],
                        "total_time_ms": stats["total_time_ms"]
                    })
            
            # Sort by average execution time
            slow_queries.sort(key=lambda x: x["avg_time_ms"], reverse=True)
            return slow_queries
    
    def get_query_stats_summary(self) -> Dict[str, Any]:
        """Get summary of query performance statistics"""
        with self._lock:
            if not self.query_stats:
                return {"total_queries": 0, "cache_stats": self.query_cache.get_stats()}
            
            total_executions = sum(stats["execution_count"] for stats in self.query_stats.values())
            total_time = sum(stats["total_time_ms"] for stats in self.query_stats.values())
            avg_time = total_time / total_executions if total_executions > 0 else 0
            
            execution_times = []
            for stats in self.query_stats.values():
                avg_query_time = stats["total_time_ms"] / stats["execution_count"]
                execution_times.append(avg_query_time)
            
            return {
                "total_unique_queries": len(self.query_stats),
                "total_executions": total_executions,
                "average_execution_time_ms": avg_time,
                "slowest_average_time_ms": max(execution_times) if execution_times else 0,
                "fastest_average_time_ms": min(execution_times) if execution_times else 0,
                "cache_stats": self.query_cache.get_stats()
            }


class AsyncBatchProcessor:
    """Batch processing for improved performance"""
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._batches: Dict[str, List[Any]] = {}
        self._processors: Dict[str, Callable] = {}
        self._last_flush: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
        
        # Start background flush task
        self._flush_task = None
        self._start_flush_task()
    
    def register_processor(self, batch_type: str, processor_func: Callable):
        """Register a batch processor function"""
        self._processors[batch_type] = processor_func
        self._batches[batch_type] = []
        self._last_flush[batch_type] = datetime.utcnow()
    
    def _ensure_flush_task(self):
        """Ensure flush task is running if there's an event loop"""
        if self._flush_task is None:
            self._start_flush_task()
    
    async def add_item(self, batch_type: str, item: Any):
        """Add item to batch"""
        # Ensure flush task is running
        self._ensure_flush_task()
        
        async with self._lock:
            if batch_type not in self._batches:
                raise ValueError(f"Unknown batch type: {batch_type}")
            
            self._batches[batch_type].append(item)
            
            # Check if batch is full
            if len(self._batches[batch_type]) >= self.batch_size:
                await self._flush_batch(batch_type)
    
    async def _flush_batch(self, batch_type: str):
        """Flush a specific batch"""
        if batch_type not in self._batches or not self._batches[batch_type]:
            return
        
        batch = self._batches[batch_type].copy()
        self._batches[batch_type].clear()
        self._last_flush[batch_type] = datetime.utcnow()
        
        processor = self._processors[batch_type]
        
        try:
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(processor):
                await processor(batch)
            else:
                processor(batch)
            
            processing_time = (time.time() - start_time) * 1000
            
            monitoring.metrics.record_histogram(
                "batch_processing_duration_ms",
                processing_time,
                labels={"batch_type": batch_type}
            )
            
            monitoring.metrics.increment_counter(
                "batch_items_processed",
                len(batch),
                labels={"batch_type": batch_type}
            )
            
            logger.debug(f"Processed batch of {len(batch)} {batch_type} items in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Error processing {batch_type} batch: {e}")
            
            monitoring.metrics.increment_counter(
                "batch_processing_errors",
                labels={"batch_type": batch_type}
            )
    
    def _start_flush_task(self):
        """Start background task to flush batches periodically"""
        async def flush_task():
            while True:
                try:
                    await asyncio.sleep(self.flush_interval)
                    await self._flush_all_batches()
                except Exception as e:
                    logger.error(f"Error in batch flush task: {e}")
        
        if self._flush_task is None:
            try:
                # Only create task if there's a running event loop
                self._flush_task = asyncio.create_task(flush_task())
            except RuntimeError:
                # No running event loop, defer task creation
                logger.debug("No running event loop, deferring flush task creation")
                self._flush_task = None
    
    async def _flush_all_batches(self):
        """Flush all batches that have pending items"""
        async with self._lock:
            now = datetime.utcnow()
            
            for batch_type in list(self._batches.keys()):
                # Check if batch has items and enough time has passed
                if (self._batches[batch_type] and 
                    (now - self._last_flush[batch_type]).total_seconds() >= self.flush_interval):
                    await self._flush_batch(batch_type)
    
    async def flush_all(self):
        """Manually flush all batches"""
        async with self._lock:
            for batch_type in list(self._batches.keys()):
                if self._batches[batch_type]:
                    await self._flush_batch(batch_type)
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        with self._lock:
            stats = {}
            for batch_type, batch in self._batches.items():
                stats[batch_type] = {
                    "pending_items": len(batch),
                    "last_flush": self._last_flush[batch_type].isoformat(),
                    "batch_size": self.batch_size
                }
            return stats


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.memory_cache = MemoryCache(max_size=2000, default_ttl=600)  # 10 minute default TTL
        self.query_optimizer = QueryOptimizer()
        self.batch_processor = AsyncBatchProcessor(batch_size=50, flush_interval=10.0)
        
        # Register default batch processors
        self._register_default_processors()
    
    def _register_default_processors(self):
        """Register default batch processors"""
        
        async def process_audit_logs(batch: List[Dict[str, Any]]):
            """Process batch of audit log entries"""
            # In a real implementation, this would write to audit log storage
            logger.info(f"Processing batch of {len(batch)} audit log entries")
            monitoring.metrics.increment_counter("audit_logs_processed", len(batch))
        
        async def process_metrics(batch: List[Dict[str, Any]]):
            """Process batch of metrics"""
            # In a real implementation, this would write to metrics storage
            logger.debug(f"Processing batch of {len(batch)} metrics")
            monitoring.metrics.increment_counter("metrics_processed", len(batch))
        
        self.batch_processor.register_processor("audit_logs", process_audit_logs)
        self.batch_processor.register_processor("metrics", process_metrics)
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cache_stats": self.memory_cache.get_stats(),
            "query_stats": self.query_optimizer.get_query_stats_summary(),
            "batch_stats": self.batch_processor.get_batch_stats(),
            "slow_queries": self.query_optimizer.get_slow_queries(threshold_ms=500)
        }
    
    def cache_decorator(self, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.memory_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Cache the result
                self.memory_cache.set(cache_key, result, ttl)
                
                # Record metrics
                monitoring.metrics.record_histogram(
                    "cached_function_duration_ms",
                    execution_time,
                    labels={"function": func.__name__}
                )
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_result = self.memory_cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                
                # Cache the result
                self.memory_cache.set(cache_key, result, ttl)
                
                # Record metrics
                monitoring.metrics.record_histogram(
                    "cached_function_duration_ms",
                    execution_time,
                    labels={"function": func.__name__}
                )
                
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
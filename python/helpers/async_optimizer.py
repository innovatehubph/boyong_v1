"""
Async Performance Optimizer for Pareng Boyong
Provides optimizations for async operations and concurrency
"""

import asyncio
import functools
import time
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading

T = TypeVar('T')

class AsyncOptimizer:
    """Provides various async optimizations"""
    
    # Shared thread pool for I/O bound operations
    _thread_pool = None
    # Shared process pool for CPU bound operations  
    _process_pool = None
    _lock = threading.Lock()
    
    @classmethod
    def get_thread_pool(cls, max_workers: int = 10) -> ThreadPoolExecutor:
        """Get or create shared thread pool"""
        if cls._thread_pool is None:
            with cls._lock:
                if cls._thread_pool is None:
                    cls._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        return cls._thread_pool
    
    @classmethod
    def get_process_pool(cls, max_workers: int = 4) -> ProcessPoolExecutor:
        """Get or create shared process pool"""
        if cls._process_pool is None:
            with cls._lock:
                if cls._process_pool is None:
                    cls._process_pool = ProcessPoolExecutor(max_workers=max_workers)
        return cls._process_pool

async def run_with_timeout(
    coro: Coroutine[Any, Any, T],
    timeout: float,
    default: Optional[T] = None
) -> T:
    """Run coroutine with timeout, return default on timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return default

async def run_concurrent_tasks(
    tasks: list[Coroutine],
    max_concurrent: int = 5,
    return_exceptions: bool = True
) -> list[Any]:
    """Run tasks with controlled concurrency"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_semaphore(task):
        async with semaphore:
            return await task
    
    wrapped_tasks = [run_with_semaphore(task) for task in tasks]
    return await asyncio.gather(*wrapped_tasks, return_exceptions=return_exceptions)

def async_cached(ttl: float = 60):
    """Decorator to cache async function results with TTL"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_times = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check if cached and not expired
            if key in cache:
                if time.time() - cache_times[key] < ttl:
                    return cache[key]
            
            # Execute and cache
            result = await func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = time.time()
            
            # Clean old entries
            current_time = time.time()
            expired_keys = [k for k, t in cache_times.items() if current_time - t > ttl]
            for k in expired_keys:
                del cache[k]
                del cache_times[k]
            
            return result
        
        return wrapper
    return decorator

async def run_in_thread(func: Callable, *args, **kwargs) -> Any:
    """Run blocking function in thread pool"""
    loop = asyncio.get_event_loop()
    executor = AsyncOptimizer.get_thread_pool()
    return await loop.run_in_executor(executor, func, *args, **kwargs)

async def run_in_process(func: Callable, *args, **kwargs) -> Any:
    """Run CPU-intensive function in process pool"""
    loop = asyncio.get_event_loop()
    executor = AsyncOptimizer.get_process_pool()
    return await loop.run_in_executor(executor, func, *args, **kwargs)

class AsyncBatcher:
    """Batch async operations for efficiency"""
    
    def __init__(self, batch_size: int = 10, max_wait: float = 0.1):
        self.batch_size = batch_size
        self.max_wait = max_wait
        self.queue = []
        self.results = {}
        self.lock = asyncio.Lock()
        self.batch_event = asyncio.Event()
        
    async def add(self, key: str, coro: Coroutine) -> Any:
        """Add coroutine to batch and wait for result"""
        async with self.lock:
            self.queue.append((key, coro))
            
            if len(self.queue) >= self.batch_size:
                await self._process_batch()
            else:
                # Schedule batch processing after max_wait
                asyncio.create_task(self._delayed_batch())
        
        # Wait for result
        while key not in self.results:
            await asyncio.sleep(0.01)
        
        return self.results.pop(key)
    
    async def _delayed_batch(self):
        """Process batch after delay"""
        await asyncio.sleep(self.max_wait)
        async with self.lock:
            if self.queue:
                await self._process_batch()
    
    async def _process_batch(self):
        """Process current batch"""
        if not self.queue:
            return
        
        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]
        
        # Run batch concurrently
        keys = [k for k, _ in batch]
        coros = [c for _, c in batch]
        results = await asyncio.gather(*coros, return_exceptions=True)
        
        # Store results
        for key, result in zip(keys, results):
            self.results[key] = result

class AsyncRetry:
    """Retry async operations with exponential backoff"""
    
    @staticmethod
    async def retry(
        coro_func: Callable[..., Coroutine],
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        *args,
        **kwargs
    ) -> Any:
        """Retry coroutine function with exponential backoff"""
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return await coro_func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    await asyncio.sleep(min(delay, max_delay))
                    delay *= backoff_factor
        
        raise last_exception

# Convenience functions
async def gather_with_progress(
    coros: list[Coroutine],
    callback: Optional[Callable[[int, int], None]] = None
) -> list[Any]:
    """Gather coroutines with progress callback"""
    total = len(coros)
    completed = 0
    results = []
    
    async def wrapped_coro(coro):
        nonlocal completed
        result = await coro
        completed += 1
        if callback:
            callback(completed, total)
        return result
    
    wrapped = [wrapped_coro(c) for c in coros]
    return await asyncio.gather(*wrapped)

# Global optimizer instance
optimizer = AsyncOptimizer()
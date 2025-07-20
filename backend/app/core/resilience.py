"""
Error Handling and Resilience System for DiagnoAssist Backend

This module provides comprehensive error handling, retry mechanisms,
circuit breakers, and system resilience patterns.
"""
import asyncio
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from enum import Enum
from dataclasses import dataclass
from functools import wraps
import logging

from app.core.monitoring import monitoring
from app.core.exceptions import DiagnoAssistException

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class RetryStrategy(str, Enum):
    """Retry strategies"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    RANDOM = "random"


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_factor: float = 2.0
    jitter: bool = True
    retryable_exceptions: List[type] = None
    
    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [ConnectionError, TimeoutError, Exception]


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60
    recovery_timeout_seconds: int = 30
    monitored_exceptions: List[type] = None
    
    def __post_init__(self):
        if self.monitored_exceptions is None:
            self.monitored_exceptions = [ConnectionError, TimeoutError, Exception]


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state_changed_time = datetime.utcnow()
        
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                self._record_rejected_call()
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            execution_time = (time.time() - start_time) * 1000
            self._record_success(execution_time)
            
            return result
            
        except Exception as e:
            if self._is_monitored_exception(e):
                self._record_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout_seconds
    
    def _transition_to_half_open(self):
        """Transition circuit breaker to half-open state"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.state_changed_time = datetime.utcnow()
        
        logger.info(f"Circuit breaker {self.name} transitioned to HALF_OPEN")
        monitoring.metrics.increment_counter(
            "circuit_breaker_state_changes",
            labels={"circuit": self.name, "new_state": "half_open"}
        )
    
    def _record_success(self, execution_time_ms: float):
        """Record successful execution"""
        self.success_count += 1
        
        monitoring.metrics.record_histogram(
            "circuit_breaker_call_duration_ms",
            execution_time_ms,
            labels={"circuit": self.name, "outcome": "success"}
        )
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    def _record_failure(self, exception: Exception):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        monitoring.metrics.increment_counter(
            "circuit_breaker_failures",
            labels={"circuit": self.name, "exception": type(exception).__name__}
        )
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to_open()
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state transitions back to open
            self._transition_to_open()
    
    def _transition_to_open(self):
        """Transition circuit breaker to open state"""
        self.state = CircuitState.OPEN
        self.state_changed_time = datetime.utcnow()
        
        logger.warning(f"Circuit breaker {self.name} transitioned to OPEN after {self.failure_count} failures")
        monitoring.metrics.increment_counter(
            "circuit_breaker_state_changes",
            labels={"circuit": self.name, "new_state": "open"}
        )
    
    def _transition_to_closed(self):
        """Transition circuit breaker to closed state"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.state_changed_time = datetime.utcnow()
        
        logger.info(f"Circuit breaker {self.name} transitioned to CLOSED")
        monitoring.metrics.increment_counter(
            "circuit_breaker_state_changes",
            labels={"circuit": self.name, "new_state": "closed"}
        )
    
    def _record_rejected_call(self):
        """Record rejected call due to open circuit"""
        monitoring.metrics.increment_counter(
            "circuit_breaker_rejections",
            labels={"circuit": self.name}
        )
    
    def _is_monitored_exception(self, exception: Exception) -> bool:
        """Check if exception should be monitored by circuit breaker"""
        return any(isinstance(exception, exc_type) for exc_type in self.config.monitored_exceptions)
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state information"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "state_changed_time": self.state_changed_time.isoformat(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "recovery_timeout_seconds": self.config.recovery_timeout_seconds
            }
        }


class CircuitBreakerOpenError(DiagnoAssistException):
    """Exception raised when circuit breaker is open"""
    pass


class RetryExecutor:
    """Retry mechanism with various strategies"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                start_time = time.time()
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000
                
                # Record successful execution
                monitoring.metrics.record_histogram(
                    "retry_execution_duration_ms",
                    execution_time,
                    labels={"attempt": str(attempt + 1), "outcome": "success"}
                )
                
                if attempt > 0:
                    monitoring.metrics.increment_counter(
                        "retry_successes",
                        labels={"attempts": str(attempt + 1)}
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e):
                    logger.debug(f"Non-retryable exception: {type(e).__name__}")
                    raise
                
                # Check if this was the last attempt
                if attempt == self.config.max_attempts - 1:
                    monitoring.metrics.increment_counter(
                        "retry_exhausted",
                        labels={"attempts": str(self.config.max_attempts)}
                    )
                    break
                
                # Calculate delay and wait
                delay_ms = self._calculate_delay(attempt)
                
                logger.debug(f"Retry attempt {attempt + 1} failed: {e}. Retrying in {delay_ms}ms")
                
                monitoring.metrics.increment_counter(
                    "retry_attempts",
                    labels={"attempt": str(attempt + 1), "exception": type(e).__name__}
                )
                
                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000)
        
        # All attempts failed
        raise last_exception
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if exception is retryable"""
        return any(isinstance(exception, exc_type) for exc_type in self.config.retryable_exceptions)
    
    def _calculate_delay(self, attempt: int) -> int:
        """Calculate delay for retry attempt"""
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay_ms
            
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay_ms * (self.config.backoff_factor ** attempt)
            
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay_ms * (attempt + 1)
            
        elif self.config.strategy == RetryStrategy.RANDOM:
            delay = random.randint(self.config.base_delay_ms, self.config.max_delay_ms)
            
        else:
            delay = self.config.base_delay_ms
        
        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay_ms)
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            jitter = random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay + jitter)
        
        return int(delay)


class BulkheadPattern:
    """Bulkhead isolation pattern for resource separation"""
    
    def __init__(self, name: str, max_concurrent: int = 10):
        self.name = name
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_calls = 0
        self._total_calls = 0
        self._rejected_calls = 0
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with bulkhead isolation"""
        if self._semaphore.locked():
            self._rejected_calls += 1
            monitoring.metrics.increment_counter(
                "bulkhead_rejections",
                labels={"bulkhead": self.name}
            )
            raise BulkheadFullError(f"Bulkhead {self.name} is full")
        
        async with self._semaphore:
            self._active_calls += 1
            self._total_calls += 1
            
            try:
                start_time = time.time()
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                execution_time = (time.time() - start_time) * 1000
                
                monitoring.metrics.record_histogram(
                    "bulkhead_execution_duration_ms",
                    execution_time,
                    labels={"bulkhead": self.name}
                )
                
                return result
                
            finally:
                self._active_calls -= 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics"""
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "active_calls": self._active_calls,
            "total_calls": self._total_calls,
            "rejected_calls": self._rejected_calls,
            "utilization_percent": (self._active_calls / self.max_concurrent) * 100
        }


class BulkheadFullError(DiagnoAssistException):
    """Exception raised when bulkhead is full"""
    pass


class TimeoutExecutor:
    """Timeout wrapper for function execution"""
    
    def __init__(self, timeout_seconds: float):
        self.timeout_seconds = timeout_seconds
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with timeout"""
        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout_seconds)
            else:
                # For sync functions, run in executor with timeout
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, func, *args, **kwargs),
                    timeout=self.timeout_seconds
                )
            
            monitoring.metrics.increment_counter(
                "timeout_executor_success",
                labels={"timeout": str(self.timeout_seconds)}
            )
            
            return result
            
        except asyncio.TimeoutError:
            monitoring.metrics.increment_counter(
                "timeout_executor_timeouts",
                labels={"timeout": str(self.timeout_seconds)}
            )
            raise TimeoutError(f"Function execution timed out after {self.timeout_seconds} seconds")


class ResilienceManager:
    """Central resilience pattern manager"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.bulkheads: Dict[str, BulkheadPattern] = {}
        self._default_retry_config = RetryConfig()
    
    def get_circuit_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.circuit_breakers:
            config = config or CircuitBreakerConfig()
            self.circuit_breakers[name] = CircuitBreaker(name, config)
        
        return self.circuit_breakers[name]
    
    def get_bulkhead(self, name: str, max_concurrent: int = 10) -> BulkheadPattern:
        """Get or create bulkhead"""
        if name not in self.bulkheads:
            self.bulkheads[name] = BulkheadPattern(name, max_concurrent)
        
        return self.bulkheads[name]
    
    def resilient_call(
        self,
        circuit_breaker_name: Optional[str] = None,
        retry_config: Optional[RetryConfig] = None,
        timeout_seconds: Optional[float] = None,
        bulkhead_name: Optional[str] = None,
        bulkhead_max_concurrent: int = 10
    ):
        """Decorator for resilient function calls"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create execution chain
                execution_func = func
                
                # Add timeout if specified
                if timeout_seconds:
                    timeout_executor = TimeoutExecutor(timeout_seconds)
                    original_func = execution_func
                    execution_func = lambda *a, **k: timeout_executor.execute(original_func, *a, **k)
                
                # Add retry if specified
                if retry_config:
                    retry_executor = RetryExecutor(retry_config)
                    original_func = execution_func
                    execution_func = lambda *a, **k: retry_executor.execute(original_func, *a, **k)
                
                # Add bulkhead if specified
                if bulkhead_name:
                    bulkhead = self.get_bulkhead(bulkhead_name, bulkhead_max_concurrent)
                    original_func = execution_func
                    execution_func = lambda *a, **k: bulkhead.execute(original_func, *a, **k)
                
                # Add circuit breaker if specified
                if circuit_breaker_name:
                    circuit_breaker = self.get_circuit_breaker(circuit_breaker_name)
                    original_func = execution_func
                    execution_func = lambda *a, **k: circuit_breaker.call(original_func, *a, **k)
                
                # Execute with all resilience patterns
                return await execution_func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall resilience system status"""
        circuit_breaker_status = {}
        for name, cb in self.circuit_breakers.items():
            circuit_breaker_status[name] = cb.get_state()
        
        bulkhead_status = {}
        for name, bh in self.bulkheads.items():
            bulkhead_status[name] = bh.get_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "circuit_breakers": circuit_breaker_status,
            "bulkheads": bulkhead_status,
            "total_circuit_breakers": len(self.circuit_breakers),
            "total_bulkheads": len(self.bulkheads),
            "open_circuit_breakers": [
                name for name, cb in self.circuit_breakers.items()
                if cb.state == CircuitState.OPEN
            ]
        }


# Global resilience manager instance
resilience_manager = ResilienceManager()


def resilient(
    circuit_breaker: Optional[str] = None,
    retry_attempts: int = 3,
    retry_delay_ms: int = 1000,
    timeout_seconds: Optional[float] = None,
    bulkhead: Optional[str] = None,
    bulkhead_size: int = 10
):
    """Simple decorator for adding resilience to functions"""
    retry_config = RetryConfig(
        max_attempts=retry_attempts,
        base_delay_ms=retry_delay_ms
    ) if retry_attempts > 1 else None
    
    return resilience_manager.resilient_call(
        circuit_breaker_name=circuit_breaker,
        retry_config=retry_config,
        timeout_seconds=timeout_seconds,
        bulkhead_name=bulkhead,
        bulkhead_max_concurrent=bulkhead_size
    )
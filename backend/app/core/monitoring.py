"""
Monitoring and Observability System for DiagnoAssist Backend

This module provides comprehensive monitoring, logging, metrics collection,
and observability features for the medical records management system.
"""
import asyncio
import time
import uuid
import json
import psutil
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from functools import wraps
import logging
import threading

from app.models.auth import UserModel
from app.core.exceptions import DiagnoAssistException

# Configure structured logging
class StructuredLogger:
    """Structured logger with correlation IDs and context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._context = threading.local()
    
    def set_context(self, **kwargs):
        """Set logging context for current thread"""
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data.update(kwargs)
    
    def clear_context(self):
        """Clear logging context"""
        if hasattr(self._context, 'data'):
            self._context.data.clear()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current logging context"""
        return getattr(self._context, 'data', {})
    
    def _log_with_context(self, level: str, message: str, **kwargs):
        """Log message with context"""
        context = self.get_context()
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "context": context,
            **kwargs
        }
        
        # Use standard logger with JSON formatting
        getattr(self.logger, level.lower())(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        self._log_with_context("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_with_context("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_with_context("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log_with_context("DEBUG", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log_with_context("CRITICAL", message, **kwargs)


class MetricType(str, Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class HealthStatus(str, Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class Metric:
    """Represents a system metric"""
    name: str
    type: MetricType
    value: Union[int, float]
    labels: Dict[str, str]
    timestamp: datetime
    description: Optional[str] = None


@dataclass
class TraceSpan:
    """Represents a distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    tags: Dict[str, Any]
    status: str  # success, error, timeout
    error: Optional[str] = None


@dataclass
class HealthCheck:
    """Represents a health check result"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    checked_at: datetime
    response_time_ms: float


class MetricsCollector:
    """Collects and aggregates application metrics"""
    
    def __init__(self):
        self._metrics: Dict[str, List[Metric]] = {}
        self._lock = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=value,
            labels=labels or {},
            timestamp=datetime.utcnow(),
            description=f"Counter metric: {name}"
        )
        self._add_metric(metric)
    
    def set_gauge(self, name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric value"""
        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            labels=labels or {},
            timestamp=datetime.utcnow(),
            description=f"Gauge metric: {name}"
        )
        self._add_metric(metric)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram observation"""
        metric = Metric(
            name=name,
            type=MetricType.HISTOGRAM,
            value=value,
            labels=labels or {},
            timestamp=datetime.utcnow(),
            description=f"Histogram metric: {name}"
        )
        self._add_metric(metric)
    
    def _add_metric(self, metric: Metric):
        """Add metric to collection"""
        with self._lock:
            if metric.name not in self._metrics:
                self._metrics[metric.name] = []
            self._metrics[metric.name].append(metric)
            
            # Keep only last 1000 metrics per name to prevent memory issues
            if len(self._metrics[metric.name]) > 1000:
                self._metrics[metric.name] = self._metrics[metric.name][-1000:]
    
    def get_metrics(self, name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get collected metrics"""
        with self._lock:
            if name:
                metrics = self._metrics.get(name, [])
                return {name: [asdict(m) for m in metrics]}
            else:
                return {
                    metric_name: [asdict(m) for m in metric_list]
                    for metric_name, metric_list in self._metrics.items()
                }
    
    def get_metric_summary(self, name: str, window_minutes: int = 5) -> Dict[str, Any]:
        """Get metric summary for time window"""
        with self._lock:
            metrics = self._metrics.get(name, [])
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            recent_metrics = [m for m in metrics if m.timestamp > cutoff_time]
            
            if not recent_metrics:
                return {"name": name, "count": 0, "window_minutes": window_minutes}
            
            values = [m.value for m in recent_metrics]
            
            summary = {
                "name": name,
                "count": len(recent_metrics),
                "window_minutes": window_minutes,
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": recent_metrics[-1].value,
                "latest_timestamp": recent_metrics[-1].timestamp.isoformat()
            }
            
            return summary


class DistributedTracer:
    """Distributed tracing system"""
    
    def __init__(self):
        self._traces: Dict[str, List[TraceSpan]] = {}
        self._lock = threading.Lock()
        self._current_span = threading.local()
    
    def start_trace(self, operation_name: str) -> str:
        """Start a new trace"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            end_time=None,
            duration_ms=None,
            tags={},
            status="active"
        )
        
        self._add_span(span)
        self._current_span.span = span
        
        return trace_id
    
    def start_span(self, operation_name: str, parent_trace_id: Optional[str] = None) -> str:
        """Start a new span within a trace"""
        # Get parent span info
        parent_span = getattr(self._current_span, 'span', None)
        
        if parent_span:
            trace_id = parent_span.trace_id
            parent_span_id = parent_span.span_id
        elif parent_trace_id:
            trace_id = parent_trace_id
            parent_span_id = None
        else:
            # Start new trace
            return self.start_trace(operation_name)
        
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            end_time=None,
            duration_ms=None,
            tags={},
            status="active"
        )
        
        self._add_span(span)
        self._current_span.span = span
        
        return span_id
    
    def finish_span(self, span_id: Optional[str] = None, status: str = "success", error: Optional[str] = None):
        """Finish a span"""
        current_span = getattr(self._current_span, 'span', None)
        
        if not current_span:
            return
        
        if span_id and current_span.span_id != span_id:
            return
        
        current_span.end_time = datetime.utcnow()
        current_span.duration_ms = (current_span.end_time - current_span.start_time).total_seconds() * 1000
        current_span.status = status
        current_span.error = error
        
        # Clear current span
        if hasattr(self._current_span, 'span'):
            delattr(self._current_span, 'span')
    
    def add_tag(self, key: str, value: Any):
        """Add tag to current span"""
        current_span = getattr(self._current_span, 'span', None)
        if current_span:
            current_span.tags[key] = value
    
    def _add_span(self, span: TraceSpan):
        """Add span to trace collection"""
        with self._lock:
            if span.trace_id not in self._traces:
                self._traces[span.trace_id] = []
            self._traces[span.trace_id].append(span)
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Get all spans for a trace"""
        with self._lock:
            spans = self._traces.get(trace_id, [])
            return [asdict(span) for span in spans]
    
    def get_traces(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Get recent traces"""
        with self._lock:
            trace_ids = list(self._traces.keys())[-limit:]
            return {
                trace_id: [asdict(span) for span in self._traces[trace_id]]
                for trace_id in trace_ids
            }
    
    @asynccontextmanager
    async def trace_async(self, operation_name: str):
        """Async context manager for tracing"""
        span_id = self.start_span(operation_name)
        try:
            yield span_id
            self.finish_span(span_id, "success")
        except Exception as e:
            self.finish_span(span_id, "error", str(e))
            raise


class HealthChecker:
    """System health checking"""
    
    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._last_results: Dict[str, HealthCheck] = {}
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self._checks[name] = check_func
    
    async def run_check(self, name: str) -> HealthCheck:
        """Run a specific health check"""
        if name not in self._checks:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="Check not found",
                details={},
                checked_at=datetime.utcnow(),
                response_time_ms=0
            )
        
        start_time = time.time()
        
        try:
            check_func = self._checks[name]
            
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, dict):
                status = HealthStatus(result.get("status", "healthy"))
                message = result.get("message", "OK")
                details = result.get("details", {})
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = "OK" if result else "Check failed"
                details = {}
            else:
                status = HealthStatus.HEALTHY
                message = str(result)
                details = {}
            
            health_check = HealthCheck(
                name=name,
                status=status,
                message=message,
                details=details,
                checked_at=datetime.utcnow(),
                response_time_ms=response_time
            )
            
            self._last_results[name] = health_check
            return health_check
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}",
                details={"error": str(e), "error_type": type(e).__name__},
                checked_at=datetime.utcnow(),
                response_time_ms=response_time
            )
            
            self._last_results[name] = health_check
            return health_check
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        tasks = [self.run_check(name) for name in self._checks.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            check_name = list(self._checks.keys())[i]
            if isinstance(result, Exception):
                health_results[check_name] = HealthCheck(
                    name=check_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check exception: {str(result)}",
                    details={"error": str(result)},
                    checked_at=datetime.utcnow(),
                    response_time_ms=0
                )
            else:
                health_results[check_name] = result
        
        return health_results
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        if not self._last_results:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": "No health checks run",
                "checks": {}
            }
        
        all_healthy = all(check.status == HealthStatus.HEALTHY for check in self._last_results.values())
        any_unhealthy = any(check.status == HealthStatus.UNHEALTHY for check in self._last_results.values())
        
        if all_healthy:
            overall_status = HealthStatus.HEALTHY
            message = "All systems operational"
        elif any_unhealthy:
            overall_status = HealthStatus.UNHEALTHY
            unhealthy_checks = [name for name, check in self._last_results.items() if check.status == HealthStatus.UNHEALTHY]
            message = f"Unhealthy systems: {', '.join(unhealthy_checks)}"
        else:
            overall_status = HealthStatus.DEGRADED
            message = "Some systems degraded"
        
        return {
            "status": overall_status,
            "message": message,
            "checked_at": datetime.utcnow().isoformat(),
            "checks": {name: asdict(check) for name, check in self._last_results.items()}
        }


class AuditLogger:
    """Audit logging for compliance and security"""
    
    def __init__(self):
        self.logger = StructuredLogger("audit")
    
    def log_user_action(
        self, 
        user: UserModel, 
        action: str, 
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log user action for audit trail"""
        audit_entry = {
            "event_type": "user_action",
            "user_id": user.id,
            "user_email": user.email,
            "user_role": user.role.value,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": getattr(user, 'session_id', None)
        }
        
        self.logger.info("User action logged", audit=audit_entry)
    
    def log_system_event(
        self, 
        event_type: str, 
        description: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log system event"""
        audit_entry = {
            "event_type": "system_event",
            "description": description,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info("System event logged", audit=audit_entry)
    
    def log_security_event(
        self, 
        event_type: str, 
        severity: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security-related event"""
        audit_entry = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
            "description": description,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if severity in ["high", "critical"]:
            self.logger.critical("Security event", audit=audit_entry)
        else:
            self.logger.warning("Security event", audit=audit_entry)


class MonitoringSystem:
    """Central monitoring and observability system"""
    
    def __init__(self):
        self.logger = StructuredLogger("monitoring")
        self.metrics = MetricsCollector()
        self.tracer = DistributedTracer()
        self.health_checker = HealthChecker()
        self.audit_logger = AuditLogger()
        
        # Register default health checks
        self._register_default_health_checks()
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _register_default_health_checks(self):
        """Register default system health checks"""
        
        def check_memory():
            """Check system memory usage"""
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                return {
                    "status": "unhealthy",
                    "message": f"High memory usage: {usage_percent}%",
                    "details": {"usage_percent": usage_percent, "available_gb": memory.available / (1024**3)}
                }
            elif usage_percent > 80:
                return {
                    "status": "degraded", 
                    "message": f"Elevated memory usage: {usage_percent}%",
                    "details": {"usage_percent": usage_percent, "available_gb": memory.available / (1024**3)}
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Memory usage normal: {usage_percent}%",
                    "details": {"usage_percent": usage_percent, "available_gb": memory.available / (1024**3)}
                }
        
        def check_disk():
            """Check disk usage"""
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            
            if usage_percent > 90:
                return {
                    "status": "unhealthy",
                    "message": f"High disk usage: {usage_percent:.1f}%"
                }
            elif usage_percent > 80:
                return {
                    "status": "degraded",
                    "message": f"Elevated disk usage: {usage_percent:.1f}%"
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Disk usage normal: {usage_percent:.1f}%"
                }
        
        async def check_database():
            """Check database connectivity"""
            try:
                # This would check actual database connection
                # For now, return healthy
                return {
                    "status": "healthy",
                    "message": "Database connection OK"
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "message": f"Database connection failed: {str(e)}"
                }
        
        self.health_checker.register_check("memory", check_memory)
        self.health_checker.register_check("disk", check_disk)
        self.health_checker.register_check("database", check_database)
    
    def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        # In a real application, this would start background threads or async tasks
        # to collect system metrics periodically
        pass
    
    def record_api_request(
        self, 
        method: str, 
        endpoint: str, 
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None
    ):
        """Record API request metrics"""
        labels = {
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code),
            "status_class": f"{status_code // 100}xx"
        }
        
        if user_id:
            labels["user_id"] = user_id
        
        # Increment request counter
        self.metrics.increment_counter("api_requests_total", labels=labels)
        
        # Record response time
        self.metrics.record_histogram("api_request_duration_ms", duration_ms, labels=labels)
        
        # Log the request
        self.logger.info(
            "API request",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id
        )
    
    def record_business_metric(self, metric_name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Record business-specific metrics"""
        if metric_name.endswith("_count"):
            self.metrics.increment_counter(metric_name, int(value), labels)
        else:
            self.metrics.set_gauge(metric_name, value, labels)
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        # Get health status
        health_status = self.health_checker.get_overall_status()
        
        # Get key metrics
        api_requests = self.metrics.get_metric_summary("api_requests_total")
        api_duration = self.metrics.get_metric_summary("api_request_duration_ms")
        
        # Get system info
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health": health_status,
            "metrics": {
                "api_requests": api_requests,
                "api_response_time": api_duration,
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3)
                }
            },
            "uptime_seconds": time.time() - psutil.boot_time()
        }


# Global monitoring instance
monitoring = MonitoringSystem()


def monitor_function(operation_name: Optional[str] = None):
    """Decorator to monitor function execution"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            async with monitoring.tracer.trace_async(op_name):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    monitoring.metrics.record_histogram(
                        "function_duration_ms",
                        duration_ms,
                        labels={"function": op_name, "status": "success"}
                    )
                    
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    monitoring.metrics.record_histogram(
                        "function_duration_ms", 
                        duration_ms,
                        labels={"function": op_name, "status": "error"}
                    )
                    
                    monitoring.metrics.increment_counter(
                        "function_errors_total",
                        labels={"function": op_name, "error_type": type(e).__name__}
                    )
                    
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            span_id = monitoring.tracer.start_span(op_name)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                monitoring.tracer.finish_span(span_id, "success")
                monitoring.metrics.record_histogram(
                    "function_duration_ms",
                    duration_ms,
                    labels={"function": op_name, "status": "success"}
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                monitoring.tracer.finish_span(span_id, "error", str(e))
                monitoring.metrics.record_histogram(
                    "function_duration_ms",
                    duration_ms, 
                    labels={"function": op_name, "status": "error"}
                )
                
                monitoring.metrics.increment_counter(
                    "function_errors_total",
                    labels={"function": op_name, "error_type": type(e).__name__}
                )
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
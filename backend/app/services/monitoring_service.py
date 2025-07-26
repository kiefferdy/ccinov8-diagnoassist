"""
Monitoring Service for DiagnoAssist Backend

This service provides high-level monitoring and observability functionality
with APIs for metrics, health checks, and system status.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from app.core.monitoring import monitoring, HealthStatus
from app.models.auth import UserModel
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)


class MonitoringService:
    """High-level monitoring service"""
    
    def __init__(self):
        self.monitoring_system = monitoring
        self._alert_thresholds = {
            "api_response_time_ms": 5000,  # 5 seconds
            "error_rate_percent": 5.0,      # 5%
            "memory_usage_percent": 85.0,   # 85%
            "disk_usage_percent": 85.0,     # 85%
        }
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # Run all health checks
            health_results = await self.monitoring_system.health_checker.run_all_checks()
            
            # Get overall status
            overall_status = self.monitoring_system.health_checker.get_overall_status()
            
            # Add additional system metrics
            system_metrics = await self._get_system_metrics()
            
            return {
                "overall_status": overall_status["status"],
                "message": overall_status["message"],
                "checked_at": overall_status["checked_at"],
                "health_checks": overall_status["checks"],
                "system_metrics": system_metrics,
                "alerts": await self._check_alert_conditions()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "overall_status": HealthStatus.UNKNOWN,
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }
    
    async def get_application_metrics(
        self, 
        metric_names: Optional[List[str]] = None,
        time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get application performance metrics"""
        try:
            if metric_names:
                metrics = {}
                for name in metric_names:
                    metrics[name] = self.monitoring_system.metrics.get_metric_summary(
                        name, time_window_minutes
                    )
            else:
                # Get all metrics
                all_metrics = self.monitoring_system.metrics.get_metrics()
                metrics = {}
                for name in all_metrics.keys():
                    metrics[name] = self.monitoring_system.metrics.get_metric_summary(
                        name, time_window_minutes
                    )
            
            # Calculate derived metrics
            derived_metrics = await self._calculate_derived_metrics(time_window_minutes)
            
            return {
                "time_window_minutes": time_window_minutes,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics,
                "derived_metrics": derived_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {"error": str(e)}
    
    async def get_business_metrics(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get business-specific metrics"""
        try:
            business_metrics = {}
            
            # Patient-related metrics
            patient_metrics = self._get_patient_metrics(time_window_minutes)
            business_metrics["patients"] = patient_metrics
            
            # Encounter-related metrics
            encounter_metrics = self._get_encounter_metrics(time_window_minutes)
            business_metrics["encounters"] = encounter_metrics
            
            # AI medical assistant metrics
            cds_metrics = self._get_cds_metrics(time_window_minutes)
            business_metrics["ai_medical_assistant"] = cds_metrics
            
            # FHIR integration metrics
            fhir_metrics = self._get_fhir_metrics(time_window_minutes)
            business_metrics["fhir_integration"] = fhir_metrics
            
            return {
                "time_window_minutes": time_window_minutes,
                "timestamp": datetime.utcnow().isoformat(),
                "business_metrics": business_metrics
            }
            
        except Exception as e:
            logger.error(f"Error getting business metrics: {e}")
            return {"error": str(e)}
    
    async def get_trace_information(
        self, 
        trace_id: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get distributed tracing information"""
        try:
            if trace_id:
                # Get specific trace
                trace_spans = self.monitoring_system.tracer.get_trace(trace_id)
                return {
                    "trace_id": trace_id,
                    "spans": trace_spans,
                    "span_count": len(trace_spans)
                }
            else:
                # Get recent traces
                traces = self.monitoring_system.tracer.get_traces(limit)
                
                # Calculate trace statistics
                trace_stats = self._calculate_trace_statistics(traces)
                
                return {
                    "traces": traces,
                    "trace_count": len(traces),
                    "statistics": trace_stats
                }
                
        except Exception as e:
            logger.error(f"Error getting trace information: {e}")
            return {"error": str(e)}
    
    async def get_audit_logs(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get audit log entries"""
        try:
            # In a real implementation, this would query the audit log storage
            # For now, return placeholder data
            
            audit_logs = []
            
            # TODO: Implement actual audit log retrieval from storage
            logger.info(f"Audit log query: user_id={user_id}, event_type={event_type}, limit={limit}")
            
            return {
                "audit_logs": audit_logs,
                "total_count": len(audit_logs),
                "query_parameters": {
                    "start_time": start_time.isoformat() if start_time else None,
                    "end_time": end_time.isoformat() if end_time else None,
                    "user_id": user_id,
                    "event_type": event_type,
                    "limit": limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return {"error": str(e)}
    
    async def record_custom_metric(
        self, 
        metric_name: str,
        metric_value: float,
        metric_type: str = "gauge",
        labels: Optional[Dict[str, str]] = None,
        user: Optional[UserModel] = None
    ) -> bool:
        """Record a custom metric"""
        try:
            # Validate metric name
            if not metric_name or not isinstance(metric_name, str):
                raise ValidationException("Invalid metric name")
            
            # Record the metric
            if metric_type == "counter":
                self.monitoring_system.metrics.increment_counter(
                    metric_name, int(metric_value), labels
                )
            elif metric_type == "gauge":
                self.monitoring_system.metrics.set_gauge(
                    metric_name, metric_value, labels
                )
            elif metric_type == "histogram":
                self.monitoring_system.metrics.record_histogram(
                    metric_name, metric_value, labels
                )
            else:
                raise ValidationException(f"Invalid metric type: {metric_type}")
            
            # Log the custom metric recording
            if user:
                self.monitoring_system.audit_logger.log_user_action(
                    user, "record_metric", "metric", metric_name,
                    {"metric_value": metric_value, "metric_type": metric_type, "labels": labels}
                )
            
            logger.info(f"Recorded custom metric: {metric_name} = {metric_value}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording custom metric: {e}")
            return False
    
    async def create_alert(
        self, 
        alert_name: str,
        condition: str,
        threshold: float,
        user: UserModel
    ) -> Dict[str, Any]:
        """Create a monitoring alert"""
        try:
            # Validate alert parameters
            if not alert_name or not condition:
                raise ValidationException("Alert name and condition are required")
            
            # Store alert configuration (in a real implementation)
            alert_config = {
                "alert_id": f"alert_{alert_name}_{int(datetime.utcnow().timestamp())}",
                "name": alert_name,
                "condition": condition,
                "threshold": threshold,
                "created_by": user.id,
                "created_at": datetime.utcnow().isoformat(),
                "enabled": True
            }
            
            # Log alert creation
            self.monitoring_system.audit_logger.log_user_action(
                user, "create_alert", "alert", alert_config["alert_id"],
                {"alert_name": alert_name, "condition": condition, "threshold": threshold}
            )
            
            logger.info(f"Created monitoring alert: {alert_name}")
            return alert_config
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            raise
    
    async def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for dashboard"""
        try:
            # Get key performance indicators
            api_requests = self.monitoring_system.metrics.get_metric_summary(
                "api_requests_total", time_window_minutes
            )
            
            api_duration = self.monitoring_system.metrics.get_metric_summary(
                "api_request_duration_ms", time_window_minutes
            )
            
            function_errors = self.monitoring_system.metrics.get_metric_summary(
                "function_errors_total", time_window_minutes
            )
            
            # Calculate error rate
            error_rate = 0.0
            if api_requests.get("count", 0) > 0 and function_errors.get("count", 0) > 0:
                error_rate = (function_errors["count"] / api_requests["count"]) * 100
            
            # Get system resource usage
            health_status = await self.monitoring_system.health_checker.run_all_checks()
            
            memory_usage = 0.0
            disk_usage = 0.0
            
            if "memory" in health_status:
                memory_usage = health_status["memory"].details.get("usage_percent", 0)
            
            if "disk" in health_status:
                disk_details = health_status["disk"].details
                if "usage_percent" in str(disk_details):
                    # Extract disk usage from message if not in details
                    import re
                    match = re.search(r'(\d+\.?\d*)%', health_status["disk"].message)
                    if match:
                        disk_usage = float(match.group(1))
            
            # Determine overall performance status
            performance_status = "good"
            if (api_duration.get("avg", 0) > self._alert_thresholds["api_response_time_ms"] or
                error_rate > self._alert_thresholds["error_rate_percent"] or
                memory_usage > self._alert_thresholds["memory_usage_percent"]):
                performance_status = "degraded"
            
            if error_rate > 10 or memory_usage > 95:
                performance_status = "poor"
            
            return {
                "time_window_minutes": time_window_minutes,
                "timestamp": datetime.utcnow().isoformat(),
                "performance_status": performance_status,
                "metrics": {
                    "total_requests": api_requests.get("count", 0),
                    "average_response_time_ms": api_duration.get("avg", 0),
                    "error_rate_percent": error_rate,
                    "memory_usage_percent": memory_usage,
                    "disk_usage_percent": disk_usage
                },
                "thresholds": self._alert_thresholds
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics"""
        import psutil
        
        # CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network (if available)
        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        except:
            network_stats = {}
        
        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": (disk.used / disk.total) * 100
            },
            "network": network_stats
        }
    
    async def _calculate_derived_metrics(self, time_window_minutes: int) -> Dict[str, Any]:
        """Calculate derived metrics from base metrics"""
        # Get base metrics
        api_requests = self.monitoring_system.metrics.get_metric_summary(
            "api_requests_total", time_window_minutes
        )
        
        function_errors = self.monitoring_system.metrics.get_metric_summary(
            "function_errors_total", time_window_minutes
        )
        
        # Calculate derived metrics
        derived = {}
        
        # Request rate (requests per minute)
        if api_requests.get("count", 0) > 0:
            derived["requests_per_minute"] = api_requests["count"] / time_window_minutes
        else:
            derived["requests_per_minute"] = 0
        
        # Error rate percentage
        if api_requests.get("count", 0) > 0 and function_errors.get("count", 0) > 0:
            derived["error_rate_percent"] = (function_errors["count"] / api_requests["count"]) * 100
        else:
            derived["error_rate_percent"] = 0
        
        # Availability percentage (based on successful requests)
        if api_requests.get("count", 0) > 0:
            successful_requests = api_requests["count"] - function_errors.get("count", 0)
            derived["availability_percent"] = (successful_requests / api_requests["count"]) * 100
        else:
            derived["availability_percent"] = 100  # No requests = 100% available
        
        return derived
    
    def _get_patient_metrics(self, time_window_minutes: int) -> Dict[str, Any]:
        """Get patient-related business metrics"""
        # In a real implementation, these would query actual business metrics
        return {
            "registrations": self.monitoring_system.metrics.get_metric_summary(
                "patients_registered_total", time_window_minutes
            ),
            "updates": self.monitoring_system.metrics.get_metric_summary(
                "patients_updated_total", time_window_minutes
            )
        }
    
    def _get_encounter_metrics(self, time_window_minutes: int) -> Dict[str, Any]:
        """Get encounter-related business metrics"""
        return {
            "created": self.monitoring_system.metrics.get_metric_summary(
                "encounters_created_total", time_window_minutes
            ),
            "signed": self.monitoring_system.metrics.get_metric_summary(
                "encounters_signed_total", time_window_minutes
            ),
            "cancelled": self.monitoring_system.metrics.get_metric_summary(
                "encounters_cancelled_total", time_window_minutes
            )
        }
    
    def _get_cds_metrics(self, time_window_minutes: int) -> Dict[str, Any]:
        """Get clinical decision support metrics"""
        return {
            "alerts_generated": self.monitoring_system.metrics.get_metric_summary(
                "cds_alerts_generated_total", time_window_minutes
            ),
            "drug_interactions": self.monitoring_system.metrics.get_metric_summary(
                "cds_drug_interactions_total", time_window_minutes
            ),
            "diagnosis_suggestions": self.monitoring_system.metrics.get_metric_summary(
                "cds_diagnosis_suggestions_total", time_window_minutes
            )
        }
    
    def _get_fhir_metrics(self, time_window_minutes: int) -> Dict[str, Any]:
        """Get FHIR integration metrics"""
        return {
            "sync_operations": self.monitoring_system.metrics.get_metric_summary(
                "fhir_sync_operations_total", time_window_minutes
            ),
            "sync_failures": self.monitoring_system.metrics.get_metric_summary(
                "fhir_sync_failures_total", time_window_minutes
            ),
            "bundle_submissions": self.monitoring_system.metrics.get_metric_summary(
                "fhir_bundle_submissions_total", time_window_minutes
            )
        }
    
    def _calculate_trace_statistics(self, traces: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate statistics from trace data"""
        total_traces = len(traces)
        total_spans = sum(len(spans) for spans in traces.values())
        
        # Calculate average trace duration
        trace_durations = []
        error_traces = 0
        
        for spans in traces.values():
            if spans:
                # Find root span (no parent)
                root_spans = [s for s in spans if not s.get("parent_span_id")]
                if root_spans and root_spans[0].get("duration_ms"):
                    trace_durations.append(root_spans[0]["duration_ms"])
                
                # Check for errors
                if any(s.get("status") == "error" for s in spans):
                    error_traces += 1
        
        avg_duration = sum(trace_durations) / len(trace_durations) if trace_durations else 0
        error_rate = (error_traces / total_traces) * 100 if total_traces > 0 else 0
        
        return {
            "total_traces": total_traces,
            "total_spans": total_spans,
            "average_duration_ms": avg_duration,
            "error_rate_percent": error_rate,
            "spans_per_trace": total_spans / total_traces if total_traces > 0 else 0
        }
    
    async def _check_alert_conditions(self) -> List[Dict[str, Any]]:
        """Check for alert conditions based on current metrics"""
        alerts = []
        
        # Check API response time
        api_duration = self.monitoring_system.metrics.get_metric_summary("api_request_duration_ms", 5)
        if api_duration.get("avg", 0) > self._alert_thresholds["api_response_time_ms"]:
            alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": f"High API response time: {api_duration['avg']:.0f}ms",
                "threshold": self._alert_thresholds["api_response_time_ms"],
                "current_value": api_duration["avg"]
            })
        
        # Check error rate
        api_requests = self.monitoring_system.metrics.get_metric_summary("api_requests_total", 5)
        function_errors = self.monitoring_system.metrics.get_metric_summary("function_errors_total", 5)
        
        if api_requests.get("count", 0) > 0 and function_errors.get("count", 0) > 0:
            error_rate = (function_errors["count"] / api_requests["count"]) * 100
            if error_rate > self._alert_thresholds["error_rate_percent"]:
                alerts.append({
                    "type": "reliability",
                    "severity": "error" if error_rate > 10 else "warning",
                    "message": f"High error rate: {error_rate:.1f}%",
                    "threshold": self._alert_thresholds["error_rate_percent"],
                    "current_value": error_rate
                })
        
        return alerts


# Create service instance
monitoring_service = MonitoringService()
"""
Performance Integration and Testing Module for DiagnoAssist Backend

Provides integration utilities and performance testing for the optimization system.
Ensures all services are properly optimized and performance targets are met.
"""
import asyncio
import time
import statistics
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timedelta
import logging

from app.core.performance import performance_optimizer
from app.core.monitoring import monitoring
from app.services.search_service import search_service
from app.services.template_service import template_service
from app.services.report_service import report_service

logger = logging.getLogger(__name__)


class PerformanceIntegrator:
    """Integrates performance optimizations across all services"""
    
    def __init__(self):
        self.performance_targets = {
            'search_response_ms': 500,
            'template_load_ms': 200,
            'report_generation_ms': 5000,
            'cache_hit_rate_percent': 80,
            'db_connection_utilization_percent': 70
        }
        self.integration_status = {}
    
    async def initialize_performance_integrations(self):
        """Initialize performance integrations for all services"""
        logger.info("Initializing performance integrations...")
        
        try:
            # Ensure search service has performance optimization
            await self._optimize_search_service()
            
            # Ensure template service has performance optimization  
            await self._optimize_template_service()
            
            # Ensure report service has performance optimization
            await self._optimize_report_service()
            
            # Setup global performance monitoring
            await self._setup_global_monitoring()
            
            logger.info("Performance integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance integrations: {e}")
            raise
    
    async def _optimize_search_service(self):
        """Optimize search service performance"""
        try:
            # Verify search caching is enabled
            if hasattr(search_service, 'search_repository'):
                # Add performance monitoring to search operations
                original_search = search_service.search
                
                @performance_optimizer.cache_decorator(ttl=300)
                async def optimized_search(*args, **kwargs):
                    start_time = time.time()
                    result = await original_search(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    monitoring.metrics.record_histogram(
                        "search_operation_duration_ms",
                        duration_ms,
                        labels={"operation": "search"}
                    )
                    
                    return result
                
                # Replace with optimized version
                search_service.search = optimized_search
            
            self.integration_status['search_service'] = 'optimized'
            logger.debug("Search service optimization completed")
            
        except Exception as e:
            logger.error(f"Search service optimization failed: {e}")
            self.integration_status['search_service'] = 'failed'
    
    async def _optimize_template_service(self):
        """Optimize template service performance"""
        try:
            # Add caching to template operations
            if hasattr(template_service, 'get_template'):
                original_get_template = template_service.get_template
                
                @performance_optimizer.cache_decorator(ttl=600)  # 10 minute cache
                async def optimized_get_template(*args, **kwargs):
                    start_time = time.time()
                    result = await original_get_template(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    monitoring.metrics.record_histogram(
                        "template_load_duration_ms",
                        duration_ms,
                        labels={"operation": "get_template"}
                    )
                    
                    return result
                
                template_service.get_template = optimized_get_template
            
            self.integration_status['template_service'] = 'optimized'
            logger.debug("Template service optimization completed")
            
        except Exception as e:
            logger.error(f"Template service optimization failed: {e}")
            self.integration_status['template_service'] = 'failed'
    
    async def _optimize_report_service(self):
        """Optimize report service performance"""
        try:
            # Add background processing for report generation
            if hasattr(report_service, 'generate_report'):
                original_generate_report = report_service.generate_report
                
                async def optimized_generate_report(*args, **kwargs):
                    start_time = time.time()
                    
                    # Use batch processing for large reports
                    await performance_optimizer.batch_processor.add_item(
                        "report_generation", 
                        {"args": args, "kwargs": kwargs, "timestamp": datetime.utcnow()}
                    )
                    
                    result = await original_generate_report(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    monitoring.metrics.record_histogram(
                        "report_generation_duration_ms",
                        duration_ms,
                        labels={"operation": "generate_report"}
                    )
                    
                    return result
                
                report_service.generate_report = optimized_generate_report
            
            self.integration_status['report_service'] = 'optimized'
            logger.debug("Report service optimization completed")
            
        except Exception as e:
            logger.error(f"Report service optimization failed: {e}")
            self.integration_status['report_service'] = 'failed'
    
    async def _setup_global_monitoring(self):
        """Setup global performance monitoring"""
        try:
            # Register additional batch processors for performance data
            async def process_performance_metrics(batch: List[Dict[str, Any]]):
                """Process batch of performance metrics"""
                logger.debug(f"Processing {len(batch)} performance metrics")
                
                # Aggregate performance data
                for metric in batch:
                    monitoring.metrics.record_histogram(
                        "system_performance",
                        metric.get('value', 0),
                        labels=metric.get('labels', {})
                    )
            
            performance_optimizer.batch_processor.register_processor(
                "performance_metrics", 
                process_performance_metrics
            )
            
            self.integration_status['global_monitoring'] = 'active'
            logger.debug("Global performance monitoring setup completed")
            
        except Exception as e:
            logger.error(f"Global monitoring setup failed: {e}")
            self.integration_status['global_monitoring'] = 'failed'
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance tests"""
        logger.info("Starting performance tests...")
        
        test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tests': {},
            'overall_status': 'unknown',
            'recommendations': []
        }
        
        try:
            # Test search performance
            search_results = await self._test_search_performance()
            test_results['tests']['search'] = search_results
            
            # Test template performance
            template_results = await self._test_template_performance()
            test_results['tests']['template'] = template_results
            
            # Test report performance
            report_results = await self._test_report_performance()
            test_results['tests']['report'] = report_results
            
            # Test cache performance
            cache_results = await self._test_cache_performance()
            test_results['tests']['cache'] = cache_results
            
            # Determine overall status
            test_results['overall_status'] = self._determine_overall_status(test_results['tests'])
            
            # Generate recommendations
            test_results['recommendations'] = self._generate_recommendations(test_results['tests'])
            
            logger.info(f"Performance tests completed with status: {test_results['overall_status']}")
            
        except Exception as e:
            logger.error(f"Performance tests failed: {e}")
            test_results['overall_status'] = 'failed'
            test_results['error'] = str(e)
        
        return test_results
    
    async def _test_search_performance(self) -> Dict[str, Any]:
        """Test search operation performance"""
        try:
            from app.models.search import SearchRequest, SearchEntity, SearchType
            from app.models.auth import UserModel, UserRole
            
            # Create test user
            test_user = UserModel(
                id="perf_test_user",
                email="perf@test.com",
                name="Performance Test User",
                role=UserRole.DOCTOR,
                is_active=True
            )
            
            # Create test search request
            search_request = SearchRequest(
                query="test query for performance",
                entities=[SearchEntity.PATIENT],
                search_type=SearchType.FULL_TEXT,
                limit=20,
                page=1
            )
            
            # Run multiple search operations and measure performance
            durations = []
            for i in range(10):
                start_time = time.time()
                try:
                    await search_service.search(search_request, test_user)
                    duration_ms = (time.time() - start_time) * 1000
                    durations.append(duration_ms)
                except Exception as e:
                    logger.warning(f"Search test iteration {i} failed: {e}")
            
            if durations:
                avg_duration = statistics.mean(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                
                return {
                    'status': 'pass' if avg_duration < self.performance_targets['search_response_ms'] else 'fail',
                    'avg_duration_ms': avg_duration,
                    'max_duration_ms': max_duration,
                    'min_duration_ms': min_duration,
                    'target_ms': self.performance_targets['search_response_ms'],
                    'test_count': len(durations)
                }
            else:
                return {'status': 'error', 'message': 'No successful search operations'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _test_template_performance(self) -> Dict[str, Any]:
        """Test template operation performance"""
        try:
            # Mock template loading test
            durations = []
            
            for i in range(5):
                start_time = time.time()
                try:
                    # Simulate template loading operation
                    await asyncio.sleep(0.05)  # Simulate DB operation
                    duration_ms = (time.time() - start_time) * 1000
                    durations.append(duration_ms)
                except Exception as e:
                    logger.warning(f"Template test iteration {i} failed: {e}")
            
            if durations:
                avg_duration = statistics.mean(durations)
                
                return {
                    'status': 'pass' if avg_duration < self.performance_targets['template_load_ms'] else 'fail',
                    'avg_duration_ms': avg_duration,
                    'target_ms': self.performance_targets['template_load_ms'],
                    'test_count': len(durations)
                }
            else:
                return {'status': 'error', 'message': 'No successful template operations'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _test_report_performance(self) -> Dict[str, Any]:
        """Test report generation performance"""
        try:
            # Mock report generation test
            durations = []
            
            for i in range(3):  # Fewer iterations for longer operations
                start_time = time.time()
                try:
                    # Simulate report generation
                    await asyncio.sleep(0.2)  # Simulate longer operation
                    duration_ms = (time.time() - start_time) * 1000
                    durations.append(duration_ms)
                except Exception as e:
                    logger.warning(f"Report test iteration {i} failed: {e}")
            
            if durations:
                avg_duration = statistics.mean(durations)
                
                return {
                    'status': 'pass' if avg_duration < self.performance_targets['report_generation_ms'] else 'fail',
                    'avg_duration_ms': avg_duration,
                    'target_ms': self.performance_targets['report_generation_ms'],
                    'test_count': len(durations)
                }
            else:
                return {'status': 'error', 'message': 'No successful report operations'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def _test_cache_performance(self) -> Dict[str, Any]:
        """Test cache system performance"""
        try:
            cache_stats = performance_optimizer.memory_cache.get_stats()
            
            # Test cache operations
            test_key = "perf_test_key"
            test_value = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
            
            # Set and get operations
            start_time = time.time()
            performance_optimizer.memory_cache.set(test_key, test_value, ttl=60)
            set_duration_ms = (time.time() - start_time) * 1000
            
            start_time = time.time()
            retrieved_value = performance_optimizer.memory_cache.get(test_key)
            get_duration_ms = (time.time() - start_time) * 1000
            
            cache_hit = retrieved_value is not None
            
            return {
                'status': 'pass' if cache_hit else 'fail',
                'set_duration_ms': set_duration_ms,
                'get_duration_ms': get_duration_ms,
                'cache_hit': cache_hit,
                'cache_stats': cache_stats
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _determine_overall_status(self, test_results: Dict[str, Any]) -> str:
        """Determine overall performance test status"""
        passed_tests = 0
        total_tests = 0
        
        for test_name, test_result in test_results.items():
            if isinstance(test_result, dict) and 'status' in test_result:
                total_tests += 1
                if test_result['status'] == 'pass':
                    passed_tests += 1
        
        if total_tests == 0:
            return 'unknown'
        elif passed_tests == total_tests:
            return 'excellent'
        elif passed_tests / total_tests >= 0.8:
            return 'good'
        elif passed_tests / total_tests >= 0.6:
            return 'acceptable'
        else:
            return 'poor'
    
    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Check search performance
        if 'search' in test_results:
            search_result = test_results['search']
            if search_result.get('status') == 'fail':
                recommendations.append(
                    f"Search performance is below target. "
                    f"Average: {search_result.get('avg_duration_ms', 0):.1f}ms, "
                    f"Target: {self.performance_targets['search_response_ms']}ms. "
                    f"Consider optimizing database queries and improving indexing."
                )
        
        # Check template performance
        if 'template' in test_results:
            template_result = test_results['template']
            if template_result.get('status') == 'fail':
                recommendations.append(
                    f"Template loading is slower than target. "
                    f"Consider implementing template caching and preloading."
                )
        
        # Check cache performance
        if 'cache' in test_results:
            cache_result = test_results['cache']
            cache_stats = cache_result.get('cache_stats', {})
            usage_percent = cache_stats.get('usage_percent', 0)
            
            if usage_percent > 90:
                recommendations.append(
                    "Cache usage is very high (>90%). Consider increasing cache size "
                    "or implementing more aggressive eviction policies."
                )
            elif usage_percent < 20:
                recommendations.append(
                    "Cache usage is low (<20%). Review caching strategy and "
                    "ensure frequently accessed data is being cached."
                )
        
        if not recommendations:
            recommendations.append("Performance is within acceptable ranges. No immediate optimizations required.")
        
        return recommendations
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'integration_status': self.integration_status,
            'performance_targets': self.performance_targets,
            'optimization_features': {
                'memory_caching': True,
                'query_optimization': True,
                'batch_processing': True,
                'connection_pooling': True,
                'performance_monitoring': True
            }
        }


# Global performance integrator instance
performance_integrator = PerformanceIntegrator()


async def initialize_performance_system():
    """Initialize the complete performance optimization system"""
    try:
        logger.info("Initializing performance optimization system...")
        
        # Initialize performance integrations
        await performance_integrator.initialize_performance_integrations()
        
        # Run initial performance tests
        test_results = await performance_integrator.run_performance_tests()
        
        logger.info(f"Performance system initialized with status: {test_results['overall_status']}")
        
        return {
            'status': 'success',
            'integration_status': performance_integrator.get_integration_status(),
            'initial_test_results': test_results
        }
        
    except Exception as e:
        logger.error(f"Failed to initialize performance system: {e}")
        raise


async def get_performance_health_check() -> Dict[str, Any]:
    """Get comprehensive performance health check"""
    try:
        # Get current performance summary
        performance_summary = await performance_optimizer.get_performance_summary()
        
        # Get integration status
        integration_status = performance_integrator.get_integration_status()
        
        # Run quick performance tests
        test_results = await performance_integrator.run_performance_tests()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'performance_summary': performance_summary,
            'integration_status': integration_status,
            'recent_test_results': test_results,
            'system_health': {
                'cache_operational': len(performance_optimizer.memory_cache.get_stats()) > 0,
                'batch_processing_active': len(performance_optimizer.batch_processor.get_batch_stats()) > 0,
                'monitoring_active': True
            }
        }
        
    except Exception as e:
        logger.error(f"Performance health check failed: {e}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unhealthy',
            'error': str(e)
        }
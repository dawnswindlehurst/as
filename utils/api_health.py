"""API health check utilities."""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp


logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    
    service_name: str
    is_healthy: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    last_check: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'service_name': self.service_name,
            'is_healthy': self.is_healthy,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'error_message': self.error_message,
            'last_check': self.last_check.isoformat(),
        }


class APIHealthChecker:
    """Health checker for multiple APIs."""
    
    def __init__(self, timeout: int = 10):
        """
        Initialize health checker.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.results: Dict[str, HealthCheckResult] = {}
    
    async def check_endpoint(
        self,
        service_name: str,
        url: str,
        method: str = 'GET',
        expected_status: int = 200
    ) -> HealthCheckResult:
        """
        Check health of a single endpoint.
        
        Args:
            service_name: Name of the service
            url: URL to check
            method: HTTP method (default: GET)
            expected_status: Expected HTTP status code
            
        Returns:
            HealthCheckResult object
        """
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(method, url) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    is_healthy = response.status == expected_status
                    
                    result = HealthCheckResult(
                        service_name=service_name,
                        is_healthy=is_healthy,
                        status_code=response.status,
                        response_time_ms=response_time_ms,
                    )
                    
                    if not is_healthy:
                        result.error_message = f"Unexpected status code: {response.status}"
                    
                    self.results[service_name] = result
                    return result
                    
        except asyncio.TimeoutError:
            result = HealthCheckResult(
                service_name=service_name,
                is_healthy=False,
                error_message=f"Timeout after {self.timeout.total}s",
            )
            self.results[service_name] = result
            return result
            
        except Exception as e:
            result = HealthCheckResult(
                service_name=service_name,
                is_healthy=False,
                error_message=str(e),
            )
            self.results[service_name] = result
            return result
    
    async def check_multiple(
        self,
        endpoints: Dict[str, str]
    ) -> Dict[str, HealthCheckResult]:
        """
        Check multiple endpoints concurrently.
        
        Args:
            endpoints: Dictionary mapping service names to URLs
            
        Returns:
            Dictionary mapping service names to HealthCheckResult
        """
        tasks = [
            self.check_endpoint(service_name, url)
            for service_name, url in endpoints.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for service_name, result in zip(endpoints.keys(), results):
            if isinstance(result, Exception):
                health_results[service_name] = HealthCheckResult(
                    service_name=service_name,
                    is_healthy=False,
                    error_message=str(result),
                )
            else:
                health_results[service_name] = result
        
        return health_results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """
        Get overall health status.
        
        Returns:
            Dictionary with overall health information
        """
        if not self.results:
            return {
                'overall_healthy': False,
                'total_services': 0,
                'healthy_services': 0,
                'unhealthy_services': 0,
                'health_percentage': 0.0,
            }
        
        total = len(self.results)
        healthy = sum(1 for r in self.results.values() if r.is_healthy)
        unhealthy = total - healthy
        
        return {
            'overall_healthy': healthy == total,
            'total_services': total,
            'healthy_services': healthy,
            'unhealthy_services': unhealthy,
            'health_percentage': (healthy / total * 100) if total > 0 else 0.0,
        }
    
    def get_results_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all results as dictionary.
        
        Returns:
            Dictionary of service names to result dictionaries
        """
        return {
            name: result.to_dict()
            for name, result in self.results.items()
        }


# Predefined endpoints for common services
DEFAULT_ENDPOINTS = {
    'VLR.gg': 'https://www.vlr.gg',
    'HLTV': 'https://www.hltv.org',
    'OpenDota': 'https://api.opendota.com/api/health',
    'Superbet': 'https://production-superbet-offer-br.freetls.fastly.net/v2/pt-BR/sports',
}


async def quick_health_check() -> Dict[str, HealthCheckResult]:
    """
    Quick health check of all default services.
    
    Returns:
        Dictionary of service names to HealthCheckResult
    """
    checker = APIHealthChecker()
    return await checker.check_multiple(DEFAULT_ENDPOINTS)

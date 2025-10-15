"""
Performance monitoring and metrics collection for the Customer Bot application.
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import asyncio

from app.utils.logger import logger


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    session_id: Optional[str] = None
    confidence_score: Optional[float] = None
    response_type: Optional[str] = None
    escalated: bool = False


@dataclass
class SystemMetrics:
    """System-wide metrics."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    requests_per_minute: float
    escalation_rate: float
    average_confidence_score: float
    active_sessions: int
    timestamp: datetime


class MetricsCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.request_history: deque = deque(maxlen=max_history)
        self.session_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.endpoint_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'success_count': 0,
            'error_count': 0
        })
        self._lock = asyncio.Lock()
    
    async def record_request(self, metrics: RequestMetrics):
        """Record a request metric."""
        async with self._lock:
            self.request_history.append(metrics)
            
            
            endpoint_key = f"{metrics.method} {metrics.endpoint}"
            self.endpoint_metrics[endpoint_key]['count'] += 1
            self.endpoint_metrics[endpoint_key]['total_time'] += metrics.response_time
            
            if 200 <= metrics.status_code < 400:
                self.endpoint_metrics[endpoint_key]['success_count'] += 1
            else:
                self.endpoint_metrics[endpoint_key]['error_count'] += 1
            
            
            if metrics.session_id:
                if metrics.session_id not in self.session_metrics:
                    self.session_metrics[metrics.session_id] = {
                        'request_count': 0,
                        'total_time': 0.0,
                        'escalations': 0,
                        'confidence_scores': []
                    }
                
                session_metrics = self.session_metrics[metrics.session_id]
                session_metrics['request_count'] += 1
                session_metrics['total_time'] += metrics.response_time
                
                if metrics.escalated:
                    session_metrics['escalations'] += 1
                
                if metrics.confidence_score is not None:
                    session_metrics['confidence_scores'].append(metrics.confidence_score)
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        async with self._lock:
            if not self.request_history:
                return SystemMetrics(
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_response_time=0.0,
                    requests_per_minute=0.0,
                    escalation_rate=0.0,
                    average_confidence_score=0.0,
                    active_sessions=len(self.session_metrics),
                    timestamp=datetime.utcnow()
                )
            
            
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_requests = [
                r for r in self.request_history 
                if r.timestamp > one_hour_ago
            ]
            
            if not recent_requests:
                recent_requests = list(self.request_history)
            
            total_requests = len(recent_requests)
            successful_requests = len([r for r in recent_requests if 200 <= r.status_code < 400])
            failed_requests = total_requests - successful_requests
            
            total_response_time = sum(r.response_time for r in recent_requests)
            average_response_time = total_response_time / total_requests if total_requests > 0 else 0.0
            
           
            if recent_requests:
                time_span = (recent_requests[-1].timestamp - recent_requests[0].timestamp).total_seconds() / 60
                requests_per_minute = total_requests / time_span if time_span > 0 else 0.0
            else:
                requests_per_minute = 0.0
            
           
            escalated_requests = len([r for r in recent_requests if r.escalated])
            escalation_rate = escalated_requests / total_requests if total_requests > 0 else 0.0
            
           
            confidence_scores = [r.confidence_score for r in recent_requests if r.confidence_score is not None]
            average_confidence_score = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            return SystemMetrics(
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                average_response_time=average_response_time,
                requests_per_minute=requests_per_minute,
                escalation_rate=escalation_rate,
                average_confidence_score=average_confidence_score,
                active_sessions=len(self.session_metrics),
                timestamp=datetime.utcnow()
            )
    
    async def get_endpoint_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics by endpoint."""
        async with self._lock:
            endpoint_stats = {}
            
            for endpoint, metrics in self.endpoint_metrics.items():
                if metrics['count'] > 0:
                    endpoint_stats[endpoint] = {
                        'total_requests': metrics['count'],
                        'success_rate': metrics['success_count'] / metrics['count'],
                        'error_rate': metrics['error_count'] / metrics['count'],
                        'average_response_time': metrics['total_time'] / metrics['count'],
                        'total_response_time': metrics['total_time']
                    }
            
            return endpoint_stats
    
    async def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific session."""
        async with self._lock:
            if session_id not in self.session_metrics:
                return None
            
            metrics = self.session_metrics[session_id].copy()
            
            # Calculate averages
            if metrics['confidence_scores']:
                metrics['average_confidence_score'] = sum(metrics['confidence_scores']) / len(metrics['confidence_scores'])
                metrics['escalation_rate'] = metrics['escalations'] / metrics['request_count']
            else:
                metrics['average_confidence_score'] = 0.0
                metrics['escalation_rate'] = 0.0
            
          
            del metrics['confidence_scores']
            
            return metrics
    
    async def cleanup_old_metrics(self, max_age_hours: int = 24):
        """Clean up old metrics data."""
        async with self._lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
        
            self.request_history = deque(
                [r for r in self.request_history if r.timestamp > cutoff_time],
                maxlen=self.max_history
            )
            
          
            logger.info(f"Cleaned up metrics older than {max_age_hours} hours")
    
    async def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring systems."""
        system_metrics = await self.get_system_metrics()
        endpoint_metrics = await self.get_endpoint_metrics()
        
        return {
            'system_metrics': asdict(system_metrics),
            'endpoint_metrics': endpoint_metrics,
            'active_sessions_count': len(self.session_metrics),
            'export_timestamp': datetime.utcnow().isoformat()
        }



metrics_collector = MetricsCollector()


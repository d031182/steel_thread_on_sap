"""
Log Intelligence Service
========================
Concrete implementation of LogAdapterInterface for runtime log analysis.

This service provides intelligence by analyzing application logs stored
in SQLite database. It implements all abstract methods from LogAdapterInterface
with real analysis logic.

Features:
- Error pattern detection (DI violations, common errors)
- Performance hotspot identification (slow queries, operations)
- Module health scoring (error rate, duration, trends)
- Time-series analysis (error spikes, trends)

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from core.interfaces.log_intelligence import LogAdapterInterface


class LogIntelligenceService(LogAdapterInterface):
    """
    Real implementation of log analysis for quality tools.
    
    This service connects to the log database and provides
    intelligent analysis of runtime behavior to enhance
    Feng Shui, Gu Wu, and Shi Fu.
    
    Usage:
        from modules.log_manager.backend.logging_service import LoggingService
        from core.services.log_intelligence import LogIntelligenceService
        
        log_service = LoggingService()
        intelligence = LogIntelligenceService(log_service)
        
        # Get error patterns
        patterns = intelligence.detect_error_patterns(hours=24)
        
        # Get module health
        health = intelligence.get_module_health('knowledge_graph')
    """
    
    def __init__(self, log_service):
        """
        Initialize log intelligence service.
        
        Args:
            log_service: LoggingService instance from log_manager module
        """
        self.log_service = log_service
        self._available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """
        Check if log service is accessible.
        
        Returns:
            True if logs can be queried, False otherwise
        """
        try:
            # Try to get log count (quick check)
            self.log_service.get_log_count()
            return True
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """
        Check if log data is available.
        
        Returns:
            True if logs are accessible, False otherwise
        """
        return self._available
    
    def get_error_count(self, hours: int = 24, module: Optional[str] = None) -> int:
        """
        Get count of ERROR level logs.
        
        Args:
            hours: Look back period in hours
            module: Filter by module name (optional)
        
        Returns:
            Number of error logs found
        """
        if not self.is_available():
            return 0
        
        try:
            start_date = (datetime.now() - timedelta(hours=hours)).isoformat()
            errors = self.log_service.get_logs(
                level='ERROR',
                start_date=start_date,
                limit=10000  # High limit to get all errors
            )
            
            if module:
                # Filter by module name in message or logger
                errors = [
                    e for e in errors
                    if module.lower() in e.get('message', '').lower() or
                       module.lower() in e.get('logger', '').lower()
                ]
            
            return len(errors)
        except Exception:
            return 0
    
    def get_error_rate(self, hours: int = 24, module: Optional[str] = None) -> float:
        """
        Calculate error rate (errors per hour).
        
        Args:
            hours: Look back period in hours
            module: Filter by module name (optional)
        
        Returns:
            Average errors per hour
        """
        if hours <= 0:
            return 0.0
        
        count = self.get_error_count(hours, module)
        return count / hours
    
    def detect_error_patterns(self, hours: int = 24) -> List[Dict]:
        """
        Detect recurring error patterns.
        
        Identifies common error types, DI violations, and runtime issues
        that appear multiple times in logs.
        
        Args:
            hours: Look back period in hours
        
        Returns:
            List of error patterns sorted by severity and frequency
        """
        if not self.is_available():
            return []
        
        try:
            start_date = (datetime.now() - timedelta(hours=hours)).isoformat()
            errors = self.log_service.get_logs(
                level='ERROR',
                start_date=start_date,
                limit=10000
            )
            
            if not errors:
                return []
            
            # Group errors by pattern
            patterns = defaultdict(lambda: {
                'count': 0,
                'locations': set(),
                'timestamps': [],
                'messages': []
            })
            
            for error in errors:
                message = error.get('message', '')
                timestamp = error.get('timestamp', '')
                
                # Extract error type and key information
                pattern_key = self._extract_error_pattern(message)
                location = self._extract_location(message)
                
                patterns[pattern_key]['count'] += 1
                if location:
                    patterns[pattern_key]['locations'].add(location)
                patterns[pattern_key]['timestamps'].append(timestamp)
                if len(patterns[pattern_key]['messages']) < 3:  # Keep sample messages
                    patterns[pattern_key]['messages'].append(message)
            
            # Convert to list and add metadata
            result = []
            for pattern, data in patterns.items():
                if data['count'] < 2:  # Only patterns that repeat
                    continue
                
                severity = self._calculate_pattern_severity(
                    pattern, data['count'], hours
                )
                
                result.append({
                    'pattern': pattern,
                    'count': data['count'],
                    'locations': sorted(list(data['locations'])),
                    'severity': severity,
                    'first_seen': min(data['timestamps']) if data['timestamps'] else '',
                    'last_seen': max(data['timestamps']) if data['timestamps'] else '',
                    'sample_messages': data['messages'][:2]  # First 2 samples
                })
            
            # Sort by severity then count
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            result.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['count']))
            
            return result
        
        except Exception as e:
            print(f"Error detecting patterns: {e}")
            return []
    
    def _extract_error_pattern(self, message: str) -> str:
        """
        Extract error pattern from message (normalize for grouping).
        
        Args:
            message: Error message
        
        Returns:
            Normalized pattern key
        """
        # Extract exception type
        exception_match = re.search(r'(\w+Error|\w+Exception):', message)
        if exception_match:
            error_type = exception_match.group(1)
            
            # Get first sentence after exception type
            remaining = message[exception_match.end():].strip()
            first_line = remaining.split('\n')[0][:100]  # First 100 chars
            
            # Remove specific values (numbers, paths with line numbers)
            normalized = re.sub(r'\d+', 'N', first_line)
            normalized = re.sub(r'line \d+', 'line N', normalized)
            
            return f"{error_type}: {normalized}"
        
        # No exception type - use first line
        first_line = message.split('\n')[0][:100]
        return first_line
    
    def _extract_location(self, message: str) -> Optional[str]:
        """
        Extract file location from error message.
        
        Args:
            message: Error message
        
        Returns:
            Location string or None
        """
        # Look for "at module/file.py:line" patterns
        location_match = re.search(r'at ([\w/\\]+\.py):(\d+)', message)
        if location_match:
            return f"{location_match.group(1)}:{location_match.group(2)}"
        
        # Look for "File 'path', line N" patterns
        location_match = re.search(r"File ['\"]([^'\"]+)['\"], line (\d+)", message)
        if location_match:
            return f"{location_match.group(1)}:{location_match.group(2)}"
        
        return None
    
    def _calculate_pattern_severity(self, pattern: str, count: int, hours: int) -> str:
        """
        Calculate severity based on pattern type and frequency.
        
        Args:
            pattern: Error pattern
            count: Number of occurrences
            hours: Time period
        
        Returns:
            Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        """
        rate = count / hours if hours > 0 else count
        
        # CRITICAL: DI violations or high frequency
        if 'AttributeError' in pattern and any(attr in pattern.lower() for attr in ['connection', 'service', 'db_path']):
            return 'CRITICAL'
        if rate > 5:  # More than 5 errors per hour
            return 'CRITICAL'
        
        # HIGH: Database errors, frequent issues
        if any(keyword in pattern for keyword in ['DatabaseError', 'IntegrityError', 'OperationalError']):
            return 'HIGH'
        if rate > 1:  # More than 1 error per hour
            return 'HIGH'
        
        # MEDIUM: Recurring but not urgent
        if count >= 5:
            return 'MEDIUM'
        
        # LOW: Occasional errors
        return 'LOW'
    
    def detect_performance_issues(self, threshold_ms: float = 1000, hours: int = 24) -> List[Dict]:
        """
        Detect slow operations from duration_ms logs.
        
        Args:
            threshold_ms: Minimum duration to flag (milliseconds)
            hours: Look back period in hours
        
        Returns:
            List of performance issues sorted by severity
        """
        if not self.is_available():
            return []
        
        try:
            start_date = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # Get all logs with duration data (WARNING level typically used for slow operations)
            slow_logs = self.log_service.get_logs(
                level='WARNING',
                start_date=start_date,
                limit=10000
            )
            
            # Group by location
            hotspots = defaultdict(lambda: {
                'durations': [],
                'count': 0
            })
            
            for log in slow_logs:
                duration = log.get('duration_ms')
                if duration and duration >= threshold_ms:
                    message = log.get('message', '')
                    location = self._extract_location(message)
                    
                    if location:
                        hotspots[location]['durations'].append(duration)
                        hotspots[location]['count'] += 1
            
            # Convert to list with stats
            result = []
            for location, data in hotspots.items():
                if not data['durations']:
                    continue
                
                avg_duration = sum(data['durations']) / len(data['durations'])
                max_duration = max(data['durations'])
                
                severity = self._calculate_performance_severity(
                    avg_duration, data['count'], hours
                )
                
                result.append({
                    'location': location,
                    'avg_duration_ms': round(avg_duration, 2),
                    'max_duration_ms': round(max_duration, 2),
                    'count': data['count'],
                    'severity': severity
                })
            
            # Sort by severity then avg duration
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
            result.sort(key=lambda x: (severity_order.get(x['severity'], 4), -x['avg_duration_ms']))
            
            return result
        
        except Exception as e:
            print(f"Error detecting performance issues: {e}")
            return []
    
    def _calculate_performance_severity(self, avg_duration: float, count: int, hours: int) -> str:
        """
        Calculate severity for performance issues.
        
        Args:
            avg_duration: Average duration in milliseconds
            count: Number of occurrences
            hours: Time period
        
        Returns:
            Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        """
        rate = count / hours if hours > 0 else count
        
        # CRITICAL: Very slow and frequent
        if avg_duration > 5000 or (avg_duration > 2000 and rate > 1):
            return 'CRITICAL'
        
        # HIGH: Slow and frequent
        if avg_duration > 3000 or (avg_duration > 1500 and rate > 0.5):
            return 'HIGH'
        
        # MEDIUM: Moderately slow
        if avg_duration > 2000 or count >= 10:
            return 'MEDIUM'
        
        # LOW: Occasionally slow
        return 'LOW'
    
    def get_module_health(self, module_name: str, hours: int = 24) -> Dict:
        """
        Calculate health metrics for a specific module.
        
        Args:
            module_name: Name of module to analyze
            hours: Look back period in hours
        
        Returns:
            Health metrics dict
        """
        if not self.is_available():
            return {
                'error_count': 0,
                'warning_count': 0,
                'error_rate': 0.0,
                'avg_duration_ms': 0.0,
                'health_score': 1.0,
                'status': 'OK'
            }
        
        try:
            # Get error and warning counts
            error_count = self.get_error_count(hours, module_name)
            
            start_date = (datetime.now() - timedelta(hours=hours)).isoformat()
            warnings = self.log_service.get_logs(
                level='WARNING',
                start_date=start_date,
                limit=10000
            )
            
            warning_count = len([
                w for w in warnings
                if module_name.lower() in w.get('message', '').lower() or
                   module_name.lower() in w.get('logger', '').lower()
            ])
            
            # Calculate error rate
            error_rate = error_count / hours if hours > 0 else 0.0
            
            # Get average duration for module operations
            durations = [
                w.get('duration_ms') for w in warnings
                if w.get('duration_ms') and (
                    module_name.lower() in w.get('message', '').lower() or
                    module_name.lower() in w.get('logger', '').lower()
                )
            ]
            avg_duration_ms = sum(durations) / len(durations) if durations else 0.0
            
            # Calculate health score (0.0-1.0)
            health_score = self._calculate_health_score(
                error_count, warning_count, error_rate, avg_duration_ms
            )
            
            # Determine status
            if health_score >= 0.8:
                status = 'OK'
            elif health_score >= 0.6:
                status = 'WARNING'
            else:
                status = 'CRITICAL'
            
            return {
                'error_count': error_count,
                'warning_count': warning_count,
                'error_rate': round(error_rate, 3),
                'avg_duration_ms': round(avg_duration_ms, 2),
                'health_score': round(health_score, 2),
                'status': status
            }
        
        except Exception as e:
            print(f"Error calculating module health: {e}")
            return {
                'error_count': 0,
                'warning_count': 0,
                'error_rate': 0.0,
                'avg_duration_ms': 0.0,
                'health_score': 1.0,
                'status': 'OK'
            }
    
    def _calculate_health_score(
        self,
        error_count: int,
        warning_count: int,
        error_rate: float,
        avg_duration_ms: float
    ) -> float:
        """
        Calculate overall health score (0.0-1.0).
        
        Args:
            error_count: Total errors
            warning_count: Total warnings
            error_rate: Errors per hour
            avg_duration_ms: Average operation duration
        
        Returns:
            Health score (1.0 = perfect, 0.0 = critical)
        """
        score = 1.0
        
        # Penalize errors (most important)
        if error_count > 0:
            score -= min(0.5, error_count * 0.05)  # Max 50% penalty
        
        # Penalize error rate
        if error_rate > 0.1:
            score -= min(0.2, error_rate * 0.1)  # Max 20% penalty
        
        # Penalize warnings (less severe)
        if warning_count > 10:
            score -= min(0.15, (warning_count - 10) * 0.01)  # Max 15% penalty
        
        # Penalize slow operations
        if avg_duration_ms > 1000:
            score -= min(0.15, (avg_duration_ms - 1000) / 10000)  # Max 15% penalty
        
        return max(0.0, score)  # Ensure non-negative
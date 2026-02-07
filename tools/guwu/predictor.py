"""
Gu Wu Failure Predictor - Stage 1 of Phase 3

Predicts which tests are likely to fail before running them.
Uses historical data + code change analysis + ML-inspired heuristics.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import ast
import re


@dataclass
class PredictionResult:
    """Result of failure prediction for a single test"""
    test_id: str
    test_name: str
    failure_probability: float  # 0.0 - 1.0
    confidence: float            # 0.0 - 1.0
    reason: str
    risk_level: str             # low/medium/high/critical
    features: Dict              # Features used in prediction
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'failure_probability': round(self.failure_probability, 3),
            'confidence': round(self.confidence, 3),
            'reason': self.reason,
            'risk_level': self.risk_level,
            'features': self.features
        }


class FailurePredictor:
    """
    ML-based test failure prediction engine.
    
    Features used for prediction:
    1. Recent failure rate (last 10 runs)
    2. Code change impact (lines modified in related files)
    3. File change patterns (which files changed)
    4. Time since last run (staleness)
    5. Historical flaky score
    6. Related test failures (module dependency graph)
    
    Prediction Algorithm:
    - Base probability = recent_failure_rate
    - Apply multipliers for risk factors
    - Confidence = data quality score
    """
    
    def __init__(self, db_path: str = "tools/guwu/metrics.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Metrics database not found: {db_path}")
    
    def predict_failures(self, test_ids: List[str], 
                        changed_files: Optional[List[str]] = None) -> List[PredictionResult]:
        """
        Predict failure probability for given tests.
        
        Args:
            test_ids: List of test IDs to predict
            changed_files: List of changed files (auto-detect if None)
        
        Returns:
            List of predictions sorted by failure probability (highest first)
        """
        if changed_files is None:
            changed_files = self._get_changed_files()
        
        predictions = []
        
        for test_id in test_ids:
            try:
                prediction = self._predict_single_test(test_id, changed_files)
                predictions.append(prediction)
            except Exception as e:
                # Fallback prediction on error
                predictions.append(PredictionResult(
                    test_id=test_id,
                    test_name=self._extract_test_name(test_id),
                    failure_probability=0.5,  # Neutral
                    confidence=0.1,           # Low confidence
                    reason=f"Prediction error: {str(e)}",
                    risk_level='unknown',
                    features={}
                ))
        
        # Sort by failure probability (highest first)
        predictions.sort(key=lambda x: x.failure_probability, reverse=True)
        
        return predictions
    
    def _predict_single_test(self, test_id: str, 
                            changed_files: List[str]) -> PredictionResult:
        """Predict failure for a single test"""
        
        # Extract features
        features = self._extract_features(test_id, changed_files)
        
        # Calculate base probability from recent failures
        base_prob = features['recent_failure_rate']
        
        # Apply multipliers
        prob = base_prob
        
        # 1. Code change impact
        if features['change_impact'] > 0.5:
            prob *= 1.5  # 50% increase if significant changes
        elif features['change_impact'] > 0.2:
            prob *= 1.2  # 20% increase if moderate changes
        
        # 2. Flaky tests are unpredictable
        if features['flaky_score'] > 0.5:
            prob *= 1.3  # 30% increase for flaky tests
        
        # 3. Stale tests (not run recently)
        if features['days_since_last_run'] > 30:
            prob *= 1.1  # 10% increase if very stale
        
        # 4. Related test failures (dependency impact)
        if features['related_failures'] > 0:
            prob *= (1 + features['related_failures'] * 0.1)  # 10% per related failure
        
        # Cap at 1.0
        prob = min(1.0, prob)
        
        # Calculate confidence (data quality score)
        confidence = self._calculate_confidence(features)
        
        # Determine risk level
        risk_level = self._classify_risk(prob, confidence)
        
        # Generate human-readable reason
        reason = self._generate_reason(features, prob)
        
        return PredictionResult(
            test_id=test_id,
            test_name=features['test_name'],
            failure_probability=prob,
            confidence=confidence,
            reason=reason,
            risk_level=risk_level,
            features=features
        )
    
    def _extract_features(self, test_id: str, 
                         changed_files: List[str]) -> Dict:
        """Extract prediction features for a test"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get test history (last 10 runs)
        cursor.execute('''
            SELECT outcome, duration, timestamp, markers
            FROM test_executions
            WHERE test_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (test_id,))
        
        history = cursor.fetchall()
        
        # Get test statistics
        cursor.execute('''
            SELECT test_name, total_runs, total_failures, total_errors,
                   avg_duration, min_duration, max_duration, flaky_score, 
                   last_failure, last_run
            FROM test_statistics
            WHERE test_id = ?
        ''', (test_id,))
        
        stats = cursor.fetchone()
        conn.close()
        
        # Calculate features
        features = {}
        
        # 1. Test metadata
        if stats:
            features['test_name'] = stats[0]      # Column 0: test_name
            features['total_runs'] = stats[1]     # Column 1: total_runs
        else:
            features['test_name'] = self._extract_test_name(test_id)
            features['total_runs'] = 0
        
        # 2. Recent failure rate
        if history:
            failures = sum(1 for h in history if h[0] in ['failed', 'error'])
            features['recent_failure_rate'] = failures / len(history)
        else:
            features['recent_failure_rate'] = 0.1  # Default: 10% if no history
        
        # 3. Flaky score (Column 7: flaky_score)
        features['flaky_score'] = float(stats[7]) if stats and stats[7] is not None else 0.0
        
        # 4. Code change impact
        test_module = self._extract_module(test_id)
        features['change_impact'] = self._calculate_change_impact(
            test_module, changed_files
        )
        
        # 5. Time since last run (Column 9: last_run)
        if stats and stats[9]:  # last_run
            last_run = datetime.fromisoformat(stats[9])
            days_since = (datetime.now() - last_run).days
            features['days_since_last_run'] = days_since
        else:
            features['days_since_last_run'] = 999  # Never run
        
        # 6. Related test failures
        features['related_failures'] = self._count_related_failures(test_module)
        
        # 7. Average duration (Column 4: avg_duration)
        features['avg_duration'] = float(stats[4]) if stats and stats[4] is not None else 0.0
        
        return features
    
    def _calculate_change_impact(self, test_module: str, 
                                 changed_files: List[str]) -> float:
        """
        Calculate impact of code changes on this test.
        
        Returns: 0.0 (no impact) to 1.0 (direct impact)
        """
        if not changed_files:
            return 0.0
        
        # Direct impact: Test's module file changed
        for changed_file in changed_files:
            changed_module = self._file_to_module(changed_file)
            
            # Exact match
            if changed_module == test_module:
                return 1.0
            
            # Partial match (parent module)
            if test_module.startswith(changed_module):
                return 0.7
            
            # Related module (same top-level package)
            test_package = test_module.split('.')[0]
            changed_package = changed_module.split('.')[0]
            if test_package == changed_package:
                return 0.3
        
        # No direct impact
        return 0.1  # Small default impact (butterfly effect)
    
    def _count_related_failures(self, test_module: str) -> int:
        """Count recent failures in related tests (same module)"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent failures in same module (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        cursor.execute('''
            SELECT COUNT(DISTINCT test_id)
            FROM test_executions
            WHERE module LIKE ?
            AND outcome IN ('failed', 'error')
            AND timestamp > ?
        ''', (f'{test_module}%', yesterday))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def _calculate_confidence(self, features: Dict) -> float:
        """
        Calculate confidence in prediction (data quality score).
        
        High confidence = lots of historical data, recent runs
        Low confidence = no history, stale data
        """
        confidence = 0.0
        
        # Factor 1: Historical data availability (40%)
        total_runs = features.get('total_runs', 0)
        if total_runs >= 10:
            confidence += 0.4
        elif total_runs >= 5:
            confidence += 0.2
        elif total_runs >= 1:
            confidence += 0.1
        
        # Factor 2: Data recency (30%)
        days_since = features.get('days_since_last_run', 999)
        if days_since < 7:
            confidence += 0.3
        elif days_since < 30:
            confidence += 0.15
        elif days_since < 90:
            confidence += 0.05
        
        # Factor 3: Change detection (30%)
        change_impact = features.get('change_impact', 0.0)
        if change_impact > 0.5:
            confidence += 0.3  # High confidence if direct changes
        elif change_impact > 0.2:
            confidence += 0.15
        else:
            confidence += 0.05  # Low confidence if no changes detected
        
        return min(1.0, confidence)
    
    def _classify_risk(self, probability: float, confidence: float) -> str:
        """Classify risk level based on probability and confidence"""
        
        # High confidence predictions
        if confidence >= 0.7:
            if probability >= 0.7:
                return 'critical'
            elif probability >= 0.4:
                return 'high'
            elif probability >= 0.2:
                return 'medium'
            else:
                return 'low'
        
        # Medium confidence predictions
        elif confidence >= 0.4:
            if probability >= 0.7:
                return 'high'
            elif probability >= 0.4:
                return 'medium'
            else:
                return 'low'
        
        # Low confidence predictions (always treat as medium)
        else:
            return 'medium'
    
    def _generate_reason(self, features: Dict, probability: float) -> str:
        """Generate human-readable reason for prediction"""
        
        reasons = []
        
        # Recent failures
        failure_rate = features['recent_failure_rate']
        if failure_rate > 0.5:
            reasons.append(f"Failed {int(failure_rate * 100)}% of recent runs")
        elif failure_rate > 0.2:
            reasons.append(f"Failed {int(failure_rate * 100)}% of recent runs")
        
        # Code changes
        change_impact = features['change_impact']
        if change_impact > 0.7:
            reasons.append("Direct code changes detected")
        elif change_impact > 0.3:
            reasons.append("Related code changes detected")
        
        # Flaky score
        flaky_score = features['flaky_score']
        if flaky_score > 0.5:
            reasons.append(f"Test is flaky (score: {flaky_score:.2f})")
        
        # Staleness
        days_since = features['days_since_last_run']
        if days_since > 30:
            reasons.append(f"Not run in {days_since} days")
        
        # Related failures
        related = features['related_failures']
        if related > 0:
            reasons.append(f"{related} related test(s) failed recently")
        
        if reasons:
            return "; ".join(reasons)
        else:
            return f"Predicted {int(probability * 100)}% failure probability"
    
    def _get_changed_files(self) -> List[str]:
        """
        Get list of changed files (uncommitted + recent commits).
        
        Uses git to detect changes.
        """
        try:
            # Get uncommitted changes
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            uncommitted = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get staged changes
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            staged = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get changes from last commit
            result = subprocess.run(
                ['git', 'diff', 'HEAD~1', '--name-only'],
                capture_output=True,
                text=True,
                check=True
            )
            recent = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Combine and deduplicate
            all_changes = list(set(uncommitted + staged + recent))
            
            # Filter Python files only
            python_files = [f for f in all_changes if f.endswith('.py')]
            
            return python_files
            
        except subprocess.CalledProcessError:
            # Git command failed (not a git repo, or no changes)
            return []
    
    def _extract_module(self, test_id: str) -> str:
        """Extract module name from test ID"""
        # test_id format: tests/unit/modules/knowledge_graph/test_api.py::test_function
        # Extract: modules.knowledge_graph
        
        parts = test_id.split('::')[0].split('/')
        
        # Find module path
        try:
            if 'modules' in parts:
                idx = parts.index('modules')
                module_parts = parts[idx:idx+2]  # ['modules', 'knowledge_graph']
                return '.'.join(module_parts)
            elif 'core' in parts:
                idx = parts.index('core')
                module_parts = parts[idx:idx+2]  # ['core', 'services']
                return '.'.join(module_parts)
        except (IndexError, ValueError):
            pass
        
        return 'unknown'
    
    def _extract_test_name(self, test_id: str) -> str:
        """Extract human-readable test name from test ID"""
        # Extract function name from test_id
        if '::' in test_id:
            return test_id.split('::')[-1]
        return test_id
    
    def _file_to_module(self, file_path: str) -> str:
        """Convert file path to module name"""
        # modules/knowledge_graph/backend/api.py → modules.knowledge_graph
        
        parts = file_path.replace('\\', '/').split('/')
        
        # Find module root
        try:
            if 'modules' in parts:
                idx = parts.index('modules')
                module_parts = parts[idx:idx+2]  # ['modules', 'knowledge_graph']
                return '.'.join(module_parts)
            elif 'core' in parts:
                idx = parts.index('core')
                module_parts = parts[idx:idx+2]  # ['core', 'services']
                return '.'.join(module_parts)
        except (IndexError, ValueError):
            pass
        
        return 'unknown'
    
    def generate_prediction_report(self, predictions: List[PredictionResult]) -> str:
        """Generate formatted report of predictions"""
        
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("GU WU FAILURE PREDICTION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTotal tests analyzed: {len(predictions)}")
        
        # Risk breakdown
        risk_counts = {}
        for pred in predictions:
            risk_counts[pred.risk_level] = risk_counts.get(pred.risk_level, 0) + 1
        
        lines.append(f"\nRisk Distribution:")
        for risk in ['critical', 'high', 'medium', 'low', 'unknown']:
            count = risk_counts.get(risk, 0)
            if count > 0:
                pct = (count / len(predictions)) * 100
                lines.append(f"  {risk.upper():10s}: {count:3d} tests ({pct:5.1f}%)")
        
        # High-risk tests (top 10)
        high_risk = [p for p in predictions if p.failure_probability >= 0.4]
        if high_risk:
            lines.append(f"\n{'-' * 80}")
            lines.append(f"HIGH-RISK TESTS (probability >= 40%)")
            lines.append(f"{'-' * 80}")
            
            for i, pred in enumerate(high_risk[:10], 1):
                lines.append(f"\n{i}. {pred.test_name}")
                lines.append(f"   Failure Probability: {pred.failure_probability:.1%}")
                lines.append(f"   Confidence: {pred.confidence:.1%}")
                lines.append(f"   Risk Level: {pred.risk_level.upper()}")
                lines.append(f"   Reason: {pred.reason}")
        
        lines.append(f"\n{'=' * 80}\n")
        
        return '\n'.join(lines)


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gu Wu Failure Predictor')
    parser.add_argument('--test-ids', nargs='+', help='Specific test IDs to predict')
    parser.add_argument('--all', action='store_true', help='Predict all tests')
    parser.add_argument('--changed-files', nargs='+', help='Manually specify changed files')
    
    args = parser.parse_args()
    
    predictor = FailurePredictor()
    
    # Get test IDs
    if args.test_ids:
        test_ids = args.test_ids
    elif args.all:
        # Get all test IDs from database
        conn = sqlite3.connect("tools/guwu/metrics.db")
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT test_id FROM test_statistics')
        test_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
    else:
        print("Error: Specify --test-ids or --all")
        exit(1)
    
    # Run predictions
    predictions = predictor.predict_failures(test_ids, args.changed_files)
    
    # Generate report
    report = predictor.generate_prediction_report(predictions)
    print(report)
    
    # Save to file
    report_path = Path("tools/guwu/prediction_report.txt")
    report_path.write_text(report, encoding='utf-8')
    print(f"Report saved to: {report_path}")
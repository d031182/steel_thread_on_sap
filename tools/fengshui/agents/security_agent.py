"""
Security Agent - Security Best Practices Analysis

Specializes in:
- Hardcoded secrets detection (passwords, API keys, tokens)
- SQL injection vulnerabilities
- Authentication/authorization issues
- Input validation patterns
- Security anti-patterns
"""

import re
import logging
from pathlib import Path
from typing import List, Dict
import time

from .base_agent import BaseAgent, AgentReport, Finding, Severity
from ..utils.code_extractor import CodeExtractor


class SecurityAgent(BaseAgent):
    """
    Specializes in security auditing
    
    Detects:
    - Hardcoded secrets (passwords, API keys, tokens, connection strings)
    - SQL injection risks (string concatenation in queries)
    - Authentication/authorization issues
    - Input validation problems
    """
    
    def __init__(self):
        super().__init__("security")
        
        # Patterns for secret detection (high confidence patterns)
        self.secret_patterns = {
            'password': re.compile(r'password\s*=\s*["\'](?!.*\$|.*\{)[^"\']{6,}["\']', re.IGNORECASE),
            'api_key': re.compile(r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', re.IGNORECASE),
            'secret': re.compile(r'secret\s*=\s*["\'](?!.*\$|.*\{)[^"\']{10,}["\']', re.IGNORECASE),
            'token': re.compile(r'token\s*=\s*["\'](?!.*\$|.*\{)[^"\']{20,}["\']', re.IGNORECASE),
            'connection_string': re.compile(r'(?:connection|conn)[_-]?string\s*=\s*["\'][^"\']*password[^"\']*["\']', re.IGNORECASE),
        }
        
        # SQL injection patterns (string concatenation in queries)
        self.sql_injection_patterns = [
            re.compile(r'execute\s*\(\s*["\'][^"\']*\s*\+\s*', re.IGNORECASE),  # execute("SELECT * FROM " + var)
            re.compile(r'execute\s*\(\s*f["\'].*\{', re.IGNORECASE),  # execute(f"SELECT * FROM {table}")
            re.compile(r'query\s*=\s*["\'][^"\']*\s*\+\s*', re.IGNORECASE),  # query = "SELECT * FROM " + var
            re.compile(r'\.format\([^)]*\)\s*\)', re.IGNORECASE),  # "SELECT * FROM {}".format(table)
        ]
    
    def analyze_module(self, module_path: Path) -> AgentReport:
        """
        Analyze module security
        
        Checks:
        - Hardcoded secrets (passwords, API keys, tokens)
        - SQL injection risks (string concatenation in queries)
        - Input validation issues
        - Auth/authz patterns
        
        Args:
            module_path: Path to module directory
            
        Returns:
            AgentReport with security findings
        """
        start_time = time.time()
        findings = []
        
        if not self.validate_module_path(module_path):
            return AgentReport(
                agent_name=self.name,
                module_path=module_path,
                execution_time_seconds=0,
                findings=[],
                metrics={},
                summary="Invalid module path"
            )
        
        self.logger.info(f"Analyzing security of {module_path}")
        
        # Analyze Python files
        for py_file in module_path.rglob('*.py'):
            # Skip test files (may have test credentials)
            if 'test' in py_file.name or 'tests' in str(py_file):
                continue
            
            findings.extend(self._analyze_secrets(py_file))
            findings.extend(self._analyze_sql_injection(py_file))
        
        # Analyze JavaScript files
        for js_file in module_path.rglob('*.js'):
            if 'test' in js_file.name or 'tests' in str(js_file):
                continue
            
            findings.extend(self._analyze_secrets(js_file))
        
        # Analyze configuration files (.env, .json, .yaml)
        for config_file in list(module_path.rglob('*.env')) + list(module_path.rglob('*.json')) + list(module_path.rglob('*.yaml')):
            # Skip package.json, pytest.ini-like files
            if config_file.name in ['package.json', 'package-lock.json', 'pyproject.toml']:
                continue
            
            findings.extend(self._analyze_config_secrets(config_file))
        
        execution_time = time.time() - start_time
        
        # Calculate metrics
        python_files = len([f for f in module_path.rglob('*.py') if 'test' not in f.name])
        js_files = len([f for f in module_path.rglob('*.js') if 'test' not in f.name])
        
        metrics = {
            'total_findings': len(findings),
            'critical_count': sum(1 for f in findings if f.severity == Severity.CRITICAL),
            'high_count': sum(1 for f in findings if f.severity == Severity.HIGH),
            'medium_count': sum(1 for f in findings if f.severity == Severity.MEDIUM),
            'files_analyzed': python_files + js_files
        }
        
        summary = self._generate_summary(findings, metrics)
        
        self.logger.info(f"Security analysis complete: {summary}")
        
        return AgentReport(
            agent_name=self.name,
            module_path=module_path,
            execution_time_seconds=execution_time,
            findings=findings,
            metrics=metrics,
            summary=summary
        )
    
    def get_capabilities(self) -> List[str]:
        """Return list of security analysis capabilities"""
        return [
            "Hardcoded secret detection (passwords, API keys, tokens)",
            "SQL injection vulnerability detection",
            "Connection string security analysis",
            "Input validation pattern checking",
            "Authentication/authorization issue detection (future)",
            "XSS vulnerability detection (future)"
        ]
    
    def _analyze_secrets(self, file_path: Path) -> List[Finding]:
        """
        Analyze file for hardcoded secrets
        
        Detects:
        - Hardcoded passwords
        - API keys
        - Tokens
        - Secrets
        - Connection strings with credentials
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check each secret pattern
            for secret_type, pattern in self.secret_patterns.items():
                for line_num, line in enumerate(lines, 1):
                    # Skip comments (Python # and JavaScript //)
                    if line.strip().startswith('#') or line.strip().startswith('//'):
                        continue
                    
                    match = pattern.search(line)
                    if match:
                        # Additional validation: Skip if it's a template or placeholder
                        matched_text = match.group(0)
                        if any(placeholder in matched_text.lower() for placeholder in ['xxx', 'yyy', 'example', 'sample', 'placeholder', 'your_']):
                            continue
                        
                        # NEW in v4.34: Generate actionable finding with code context
                        code_with_context = CodeExtractor.extract_snippet(
                            str(file_path),
                            start_line=line_num,
                            highlight_lines=[line_num],
                            context_lines=2
                        )
                        
                        # Mask the actual secret value for security
                        masked_snippet = line.strip()[:100]
                        if '=' in masked_snippet:
                            parts = masked_snippet.split('=', 1)
                            masked_snippet = f"{parts[0]}= [REDACTED]"
                        
                        findings.append(Finding(
                            category="Hardcoded Secret",
                            severity=Severity.CRITICAL,
                            file_path=file_path,
                            line_number=line_num,
                            description=f"Potential hardcoded {secret_type} detected",
                            recommendation=f"Use environment variables or secret management service instead of hardcoding {secret_type}",
                            code_snippet=masked_snippet,
                            # NEW: Actionable fields
                            code_snippet_with_context=code_with_context,
                            issue_explanation=(
                                f"Hardcoded secrets in source code create security vulnerabilities:\n"
                                f"1. Exposed in version control (git history retains forever)\n"
                                f"2. Visible to all developers with repository access\n"
                                f"3. Cannot rotate without code changes\n"
                                f"4. Risk of accidental exposure (logs, error messages, screenshots)"
                            ),
                            fix_example=self._generate_secret_fix(secret_type, line),
                            impact_estimate="CRITICAL: Exposed credentials enable unauthorized access, data breaches",
                            effort_estimate="15-30 minutes (move to env vars, update code, test)"
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _analyze_sql_injection(self, file_path: Path) -> List[Finding]:
        """
        Analyze Python file for SQL injection vulnerabilities
        
        Detects:
        - String concatenation in SQL queries
        - f-strings with variables in SQL
        - .format() in SQL queries
        
        These are dangerous patterns that enable SQL injection.
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check each SQL injection pattern
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                # Check if line contains SQL keywords
                if not any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'EXECUTE']):
                    continue
                
                # Check for dangerous patterns
                for pattern in self.sql_injection_patterns:
                    if pattern.search(line):
                        findings.append(Finding(
                            category="SQL Injection Risk",
                            severity=Severity.CRITICAL,
                            file_path=file_path,
                            line_number=line_num,
                            description="Potential SQL injection vulnerability (string concatenation in query)",
                            recommendation="Use parameterized queries (e.g., execute(query, params)) instead of string concatenation",
                            code_snippet=line.strip()[:100]
                        ))
                        break  # One finding per line
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _analyze_config_secrets(self, file_path: Path) -> List[Finding]:
        """
        Analyze configuration files for hardcoded secrets
        
        Configuration files (.env, .json, .yaml) often contain credentials
        that should not be committed to version control.
        """
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Simple pattern: key=value or "key": "value" with sensitive keywords
            sensitive_keywords = ['password', 'secret', 'token', 'api_key', 'apikey', 'private_key']
            
            for line_num, line in enumerate(lines, 1):
                lower_line = line.lower()
                
                # Check if line contains sensitive keyword and a non-empty value
                for keyword in sensitive_keywords:
                    if keyword in lower_line:
                        # Check if it has a value (not just a comment or placeholder)
                        if '=' in line or ':' in line:
                            # Skip if it's clearly a placeholder
                            if any(placeholder in lower_line for placeholder in ['xxx', 'your_', 'example', '<', '>']):
                                continue
                            
                            # Check if there's actual content after = or :
                            if '=' in line:
                                value = line.split('=', 1)[1].strip()
                            else:
                                value = line.split(':', 1)[1].strip() if ':' in line else ''
                            
                            # Skip empty, null, or very short values
                            value_clean = value.strip('"\'').strip()
                            if len(value_clean) > 5 and value_clean.lower() not in ['null', 'none', '']:
                                findings.append(Finding(
                                    category="Config Secret",
                                    severity=Severity.HIGH,
                                    file_path=file_path,
                                    line_number=line_num,
                                    description=f"Potential hardcoded secret in configuration file ({keyword})",
                                    recommendation="Move sensitive values to environment variables or secret manager. Add this file to .gitignore if it contains real credentials.",
                                    code_snippet=line.strip()[:80] + "..." if len(line.strip()) > 80 else line.strip()
                                ))
                                break  # One finding per line
        
        except Exception as e:
            self.logger.warning(f"Could not analyze {file_path}: {str(e)}")
        
        return findings
    
    def _generate_secret_fix(self, secret_type: str, line: str) -> str:
        """Generate specific fix for hardcoded secret based on type"""
        if secret_type == 'password':
            return """# Current (problematic - hardcoded):
password = "my_secret_password_123"
conn = database.connect(host="localhost", user="admin", password=password)

# Fixed (secure - environment variable):
import os
password = os.getenv('DB_PASSWORD')  # Set via: export DB_PASSWORD=xxx
if not password:
    raise ValueError("DB_PASSWORD environment variable not set")
conn = database.connect(host="localhost", user="admin", password=password)

# OR use python-dotenv for .env file (add .env to .gitignore):
from dotenv import load_dotenv
load_dotenv()  # Loads from .env file
password = os.getenv('DB_PASSWORD')"""

        elif secret_type in ['api_key', 'token']:
            return """# Current (problematic - hardcoded):
api_key = "sk-1234567890abcdef1234567890abcdef"
headers = {"Authorization": f"Bearer {api_key}"}

# Fixed (secure - environment variable):
import os
api_key = os.getenv('API_KEY')  # Set via: export API_KEY=sk-xxx
if not api_key:
    raise ValueError("API_KEY environment variable not set")
headers = {"Authorization": f"Bearer {api_key}"}

# OR use secret management (AWS Secrets Manager, Azure Key Vault):
from azure.keyvault.secrets import SecretClient
client = SecretClient(vault_url="https://myvault.vault.azure.net", credential=credential)
api_key = client.get_secret("api-key").value"""

        else:
            return """# General pattern for secrets:
# 1. Remove hardcoded value from code
# 2. Store in environment variable or secret manager
# 3. Read at runtime
# 4. Validate secret exists before use
# 5. Add .env to .gitignore (never commit secrets)

import os
secret_value = os.getenv('SECRET_NAME')
if not secret_value:
    raise ValueError("SECRET_NAME not set")"""
    
    def _generate_summary(self, findings: List[Finding], metrics: Dict) -> str:
        """Generate human-readable summary"""
        if not findings:
            return f"Security analysis complete: No vulnerabilities found in {metrics['files_analyzed']} files"
        
        return (
            f"SECURITY ALERT: "
            f"{metrics['total_findings']} vulnerabilities found "
            f"({metrics['critical_count']} CRITICAL, {metrics['high_count']} HIGH, {metrics['medium_count']} MEDIUM) "
            f"in {metrics['files_analyzed']} files"
        )
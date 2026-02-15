"""
Unit tests for SecurityAgent

Tests security analysis capabilities:
- Hardcoded secret detection (passwords, API keys, tokens)
- SQL injection vulnerability detection
- Configuration file security
- Multi-language support (Python, JavaScript)
"""

import pytest
from pathlib import Path
import tempfile

from tools.fengshui.agents.security_agent import SecurityAgent
from tools.fengshui.agents.base_agent import Severity, Finding, AgentReport


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentInitialization:
    """Test SecurityAgent initialization"""
    
    def test_init_creates_agent_with_correct_name(self):
        """Test agent initializes with correct name"""
        # ARRANGE & ACT
        agent = SecurityAgent()
        
        # ASSERT
        assert agent.name == "security"
        assert hasattr(agent, 'secret_patterns')
        assert hasattr(agent, 'sql_injection_patterns')
        assert len(agent.secret_patterns) == 5
    
    def test_get_capabilities_returns_list(self):
        """Test get_capabilities returns capability list"""
        # ARRANGE
        agent = SecurityAgent()
        
        # ACT
        capabilities = agent.get_capabilities()
        
        # ASSERT
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "Hardcoded secret detection" in capabilities[0]


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentPasswordDetection:
    """Test hardcoded password detection"""
    
    def test_detect_hardcoded_password(self):
        """Test detects hardcoded password"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "config.py"
            
            test_file.write_text(
                'DB_USER = "admin"\n'
                'DB_PASSWORD = "SuperSecret123"\n'  # Hardcoded password
                'DB_HOST = "localhost"\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(test_file)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "Hardcoded Secret"
            assert findings[0].severity == Severity.CRITICAL
            assert "password" in findings[0].description.lower()
            assert findings[0].line_number == 2
    
    def test_ignores_password_placeholders(self):
        """Test ignores placeholder passwords"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "config_template.py"
            
            test_file.write_text(
                'DB_PASSWORD = "your_password_here"\n'
                'API_KEY = "xxx-example-key-xxx"\n'
                'SECRET = "PLACEHOLDER_SECRET"\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(test_file)
            
            # ASSERT
            assert len(findings) == 0  # All placeholders, no real secrets


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentAPIKeyDetection:
    """Test API key detection"""
    
    def test_detect_hardcoded_api_key(self):
        """Test detects hardcoded API key"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "service.py"
            
            test_file.write_text(
                'import requests\n'
                'API_KEY = "sk_live_51H7d2KLz9RqM3tN8P4vX"\n'  # Looks like real key
                'headers = {"Authorization": f"Bearer {API_KEY}"}\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(test_file)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "Hardcoded Secret"
            assert findings[0].severity == Severity.CRITICAL
            assert "api" in findings[0].description.lower()
            assert findings[0].line_number == 2


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentTokenDetection:
    """Test token detection"""
    
    def test_detect_hardcoded_token(self):
        """Test detects hardcoded token"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "auth.py"
            
            test_file.write_text(
                'def get_auth():\n'
                '    token = "ghp_1234567890abcdefghijklmnopqrst"\n'  # GitHub token format
                '    return token\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(test_file)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "Hardcoded Secret"
            assert "token" in findings[0].description.lower()


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentSQLInjectionDetection:
    """Test SQL injection vulnerability detection"""
    
    def test_detect_f_string_in_sql(self):
        """Test detects f-strings in SQL queries"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "queries.py"
            
            test_file.write_text(
                'def search_products(category):\n'
                '    cursor.execute(f"SELECT * FROM products WHERE category = {category}")\n',  # SQL injection!
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_sql_injection(test_file)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "SQL Injection Risk"
            assert findings[0].severity == Severity.CRITICAL
    
    def test_ignores_safe_parameterized_queries(self):
        """Test ignores safe parameterized queries"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "safe_db.py"
            
            test_file.write_text(
                'def get_user(user_id):\n'
                '    query = "SELECT * FROM users WHERE id = ?"\n'  # Safe
                '    cursor.execute(query, (user_id,))\n',  # Parameterized
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_sql_injection(test_file)
            
            # ASSERT
            assert len(findings) == 0  # No SQL injection risk


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentConfigFileAnalysis:
    """Test configuration file security analysis"""
    
    def test_detect_secrets_in_env_file(self):
        """Test detects secrets in .env files"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            env_file = module_path / ".env"
            
            env_file.write_text(
                'DB_HOST=localhost\n'
                'DB_PASSWORD=RealPassword123\n'  # Real credential
                'API_KEY=sk_live_real_key_here\n',  # Real credential
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_config_secrets(env_file)
            
            # ASSERT
            assert len(findings) == 2  # password + api_key
            assert all(f.severity == Severity.HIGH for f in findings)
            assert all(".gitignore" in f.recommendation for f in findings)
    
    def test_ignores_config_placeholders(self):
        """Test ignores placeholder values in config files"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            env_file = module_path / ".env.example"
            
            env_file.write_text(
                'DB_PASSWORD=<your_password>\n'
                'API_KEY=your_api_key_here\n'
                'SECRET=example_secret\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_config_secrets(env_file)
            
            # ASSERT
            assert len(findings) == 0  # All placeholders


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentJavaScriptSupport:
    """Test JavaScript file analysis"""
    
    def test_analyze_javascript_file_for_secrets(self):
        """Test detects secrets in JavaScript files"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            js_file = module_path / "config.js"
            
            js_file.write_text(
                'const API_KEY = "pk_live_51H7d2KLz9RqM3tN8P4vX";\n'  # Hardcoded key
                'const API_URL = "https://api.example.com";\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(js_file)
            
            # ASSERT
            assert len(findings) == 1
            assert findings[0].category == "Hardcoded Secret"
            assert "api" in findings[0].description.lower()


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentModuleAnalysis:
    """Test complete module analysis"""
    
    def test_analyze_module_with_no_vulnerabilities(self):
        """Test analysis of secure module"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            safe_file = module_path / "safe_code.py"
            
            safe_file.write_text(
                'import os\n'
                'DB_PASSWORD = os.getenv("DB_PASSWORD")\n'  # Secure: env variable
                'query = "SELECT * FROM users WHERE id = ?"\n'  # Secure: parameterized
                'cursor.execute(query, (user_id,))\n',
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.agent_name == "security"
            assert len(report.findings) == 0
            assert report.metrics['files_analyzed'] == 1
            assert "No vulnerabilities" in report.summary
    
    def test_analyze_module_with_secret_only(self):
        """Test analysis finds hardcoded secret"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # File with secret
            secret_file = module_path / "config.py"
            secret_file.write_text(
                'API_KEY = "sk_live_51H7d2KLz9RqM3tN8P4vX"\n',
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert len(report.findings) == 1
            assert report.metrics['critical_count'] == 1
            assert report.metrics['files_analyzed'] == 1
            assert "SECURITY ALERT" in report.summary
    
    def test_analyze_invalid_module_path(self):
        """Test analysis with non-existent module path"""
        # ARRANGE
        agent = SecurityAgent()
        invalid_path = Path("/nonexistent/security/module")
        
        # ACT
        report = agent.analyze_module(invalid_path)
        
        # ASSERT
        assert report.agent_name == "security"
        assert len(report.findings) == 0
        assert report.execution_time_seconds == 0
        assert "Invalid module path" in report.summary


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentTestFileSkipping:
    """Test that test files are properly skipped"""
    
    def test_skips_test_files_for_secrets(self):
        """Test skips files with 'test' in name for secret detection"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "test_auth.py"
            
            # Test files may have test credentials
            test_file.write_text(
                'TEST_PASSWORD = "test123"\n'  # Should be ignored
                'TEST_API_KEY = "sk_test_fake_key_12345678"\n',  # Should be ignored
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert len(report.findings) == 0  # Test files skipped
    
    def test_skips_tests_directory(self):
        """Test skips files in tests/ directories"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            tests_dir = module_path / "tests"
            tests_dir.mkdir()
            test_file = tests_dir / "fixtures.py"
            
            test_file.write_text(
                'FIXTURE_PASSWORD = "password123"\n',  # Test fixture
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert len(report.findings) == 0  # tests/ directory skipped


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentCommentHandling:
    """Test that comments are properly handled"""
    
    def test_ignores_secrets_in_comments(self):
        """Test ignores secrets in comments"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "commented.py"
            
            test_file.write_text(
                '# password = "DontDetectThis"\n'  # Comment
                '// api_key = "IgnoreThisToo"\n'  # JavaScript comment
                'real_var = "something_else"\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(test_file)
            
            # ASSERT
            assert len(findings) == 0  # Comments ignored


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentReportGeneration:
    """Test report generation and metrics"""
    
    def test_report_contains_all_required_fields(self):
        """Test report has all required fields"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            (module_path / "empty.py").write_text("pass", encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert hasattr(report, 'agent_name')
            assert hasattr(report, 'module_path')
            assert hasattr(report, 'execution_time_seconds')
            assert hasattr(report, 'findings')
            assert hasattr(report, 'metrics')
            assert hasattr(report, 'summary')
    
    def test_metrics_calculation_accuracy(self):
        """Test metrics are calculated correctly"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # File with CRITICAL issue (hardcoded secret)
            file1 = module_path / "secrets.py"
            file1.write_text(
                'PASSWORD = "SuperSecret123"\n',
                encoding='utf-8'
            )
            
            # File with HIGH issue (config secret)
            config_file = module_path / "config.json"
            config_file.write_text(
                '{"api_key": "real_key_12345678901234567890"}\n',
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.metrics['total_findings'] == 2
            assert report.metrics['critical_count'] == 1
            assert report.metrics['high_count'] == 1
    
    def test_summary_shows_security_alert(self):
        """Test summary includes SECURITY ALERT for vulnerabilities"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            vuln_file = module_path / "vulnerable.py"
            
            vuln_file.write_text(
                'PASSWORD = "HardcodedPassword123"\n',
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert "SECURITY ALERT" in report.summary
            assert "1 vulnerabilities" in report.summary or "1 vulnerability" in report.summary
            assert "CRITICAL" in report.summary


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentErrorHandling:
    """Test error handling and edge cases"""
    
    def test_handles_empty_module_directory(self):
        """Test handles module with no files"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert len(report.findings) == 0
            assert report.metrics['files_analyzed'] == 0
    
    def test_handles_syntax_errors_gracefully(self):
        """Test analysis continues despite file errors"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            
            # Invalid file (will cause encoding error)
            bad_file = module_path / "corrupted.py"
            bad_file.write_bytes(b'\xff\xfe')  # Invalid UTF-8
            
            # Valid file
            good_file = module_path / "good.py"
            good_file.write_text(
                'API_KEY = "sk_live_real_key_1234567890"\n',
                encoding='utf-8'
            )
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            # Should process good file despite bad file
            assert len(report.findings) >= 1  # At least the good file's secret
    
    def test_execution_time_is_recorded(self):
        """Test execution time is measured"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            (module_path / "test.py").write_text("pass", encoding='utf-8')
            
            # ACT
            report = agent.analyze_module(module_path)
            
            # ASSERT
            assert report.execution_time_seconds > 0
            assert report.execution_time_seconds < 10  # Should be fast


@pytest.mark.unit
@pytest.mark.fast
class TestSecurityAgentRecommendations:
    """Test recommendation quality"""
    
    def test_secret_recommendations_are_actionable(self):
        """Test recommendations provide clear guidance for secrets"""
        # ARRANGE
        agent = SecurityAgent()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            test_file = module_path / "config.py"
            
            test_file.write_text(
                'PASSWORD = "MySecretPassword123"\n',
                encoding='utf-8'
            )
            
            # ACT
            findings = agent._analyze_secrets(test_file)
            
            # ASSERT
            assert len(findings) == 1
            recommendation = findings[0].recommendation
            assert "environment variable" in recommendation.lower() or "secret management" in recommendation.lower()

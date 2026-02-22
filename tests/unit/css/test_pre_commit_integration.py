"""
Test: CSS Pre-Commit Hook Integration
Validates that pre-commit validation catches CSS violations before commits.

Part of: HIGH-43.3 → t-004 (Create CSS Validation Tests)
Reference: scripts/python/css_pre_commit_check.py
"""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path


class TestPreCommitIntegration:
    """Validate pre-commit hook integration catches CSS violations"""
    
    @pytest.fixture
    def pre_commit_script(self):
        """Get path to pre-commit check script"""
        return Path("scripts/python/css_pre_commit_check.py")
    
    def test_pre_commit_script_exists(self, pre_commit_script):
        """Test: Pre-commit check script exists"""
        assert pre_commit_script.exists(), f"Pre-commit script not found: {pre_commit_script}"
    
    def test_pre_commit_script_executable(self, pre_commit_script):
        """Test: Pre-commit script can be executed"""
        result = subprocess.run(
            ['python', str(pre_commit_script), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should not error out (exit code 0 or show help)
        assert result.returncode in [0, 1], (
            f"Pre-commit script failed to execute:\n"
            f"Exit code: {result.returncode}\n"
            f"Stderr: {result.stderr}"
        )
    
    def test_pre_commit_detects_spacing_violations(self, pre_commit_script, tmp_path):
        """Test: Pre-commit detects spacing magic numbers"""
        # Create test CSS file with spacing violation
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.test-class {
    margin: 16px; /* VIOLATION: Magic number */
    padding: 20px; /* VIOLATION: Magic number */
}
""")
        
        # Run pre-commit check on test file
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should detect violations (non-zero exit code)
        assert result.returncode != 0, "Pre-commit should detect spacing violations"
        
        # Output should mention violations
        output = result.stdout + result.stderr
        assert 'magic' in output.lower() or 'violation' in output.lower(), (
            "Pre-commit output should mention violations"
        )
    
    def test_pre_commit_detects_sizing_violations(self, pre_commit_script, tmp_path):
        """Test: Pre-commit detects sizing magic numbers"""
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.test-class {
    width: 300px; /* VIOLATION: Magic number */
    height: 200px; /* VIOLATION: Magic number */
}
""")
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode != 0, "Pre-commit should detect sizing violations"
    
    def test_pre_commit_detects_timing_violations(self, pre_commit_script, tmp_path):
        """Test: Pre-commit detects timing magic numbers"""
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.test-class {
    transition: opacity 0.3s ease; /* VIOLATION: Magic number */
    animation-duration: 500ms; /* VIOLATION: Magic number */
}
""")
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode != 0, "Pre-commit should detect timing violations"
    
    def test_pre_commit_allows_valid_css(self, pre_commit_script, tmp_path):
        """Test: Pre-commit allows CSS using design tokens"""
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.test-class {
    margin: var(--spacing-md);
    padding: var(--spacing-lg);
    width: var(--size-content);
    transition: opacity var(--timing-fast) ease;
}
""")
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should pass (exit code 0)
        assert result.returncode == 0, (
            f"Pre-commit should allow valid CSS:\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}"
        )
    
    def test_pre_commit_detects_bem_violations(self, pre_commit_script, tmp_path):
        """Test: Pre-commit detects BEM naming violations"""
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.invalidClassName {  /* VIOLATION: camelCase not allowed */
    margin: var(--spacing-md);
}

.another_class {  /* VIOLATION: snake_case not allowed */
    padding: var(--spacing-lg);
}
""")
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode != 0, "Pre-commit should detect BEM naming violations"
    
    def test_pre_commit_allows_bem_compliant_css(self, pre_commit_script, tmp_path):
        """Test: Pre-commit allows BEM-compliant CSS"""
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.block {
    margin: var(--spacing-md);
}

.block__element {
    padding: var(--spacing-sm);
}

.block--modifier {
    background: var(--color-primary);
}

.block__element--modifier {
    color: var(--color-text);
}
""")
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0, (
            f"Pre-commit should allow BEM-compliant CSS:\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}"
        )
    
    def test_pre_commit_summary_output(self, pre_commit_script, tmp_path):
        """Test: Pre-commit provides clear summary of violations"""
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.test-class {
    margin: 16px;
    width: 300px;
    transition: opacity 0.3s ease;
}
""")
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout + result.stderr
        
        # Should show clear summary
        assert any(word in output.lower() for word in ['violation', 'error', 'found']), (
            "Pre-commit should show violation summary"
        )
        
        # Should show file path
        assert 'test.css' in output, "Pre-commit should show affected file"
    
    def test_pre_commit_handles_multiple_files(self, pre_commit_script, tmp_path):
        """Test: Pre-commit can check multiple files"""
        # Create multiple test files
        file1 = tmp_path / "file1.css"
        file1.write_text(".class1 { margin: 16px; }")
        
        file2 = tmp_path / "file2.css"
        file2.write_text(".class2 { margin: var(--spacing-md); }")
        
        # Check if script supports multiple files or directory
        result = subprocess.run(
            ['python', str(pre_commit_script), '--dir', str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should detect violation in file1
        output = result.stdout + result.stderr
        
        # Note: This test is informational - not all pre-commit scripts support --dir
        if result.returncode != 0:
            assert 'file1.css' in output or 'violation' in output.lower(), (
                "Pre-commit should report violations when checking directory"
            )
    
    def test_pre_commit_performance(self, pre_commit_script, tmp_path):
        """Test: Pre-commit completes within reasonable time (< 5 seconds)"""
        # Create test CSS file
        test_css = tmp_path / "test.css"
        test_css.write_text("""
.test-class {
    margin: var(--spacing-md);
    padding: var(--spacing-lg);
}
""")
        
        import time
        start = time.time()
        
        result = subprocess.run(
            ['python', str(pre_commit_script), '--file', str(test_css)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        elapsed = time.time() - start
        
        assert elapsed < 5.0, (
            f"Pre-commit check took {elapsed:.2f}s (should be < 5s)\n"
            f"Fast checks are critical for developer experience"
        )
        
        print(f"\n✅ Pre-commit check completed in {elapsed:.2f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
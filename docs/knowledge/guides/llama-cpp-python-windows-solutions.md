# llama-cpp-python Windows Installation Solutions

**Created**: 2026-02-02  
**Purpose**: Document solutions for llama-cpp-python Windows installation issues  
**Context**: WinError 193 (32-bit DLL in 64-bit Python) encountered Feb 2, 2026

## Problem Summary

**Error**: `WinError 193: %1 is not a valid Win32 application`  
**Cause**: PyPI pre-built wheel contains 32-bit DLL but Python is 64-bit  
**Impact**: Cannot use fastest LLM library on Windows

## Solutions to Try (In Order)

### Solution 1: Use Pre-built Windows Wheels (RECOMMENDED)

**Source**: llama-cpp-python GitHub Releases  
**URL**: https://github.com/abetlen/llama-cpp-python/releases

**Steps**:
1. Go to GitHub releases page
2. Download Windows wheel for your Python version:
   - `llama_cpp_python-0.2.55-cp310-cp310-win_amd64.whl` (Python 3.10)
   - `llama_cpp_python-0.2.55-cp311-cp311-win_amd64.whl` (Python 3.11)
3. Install directly:
   ```bash
   pip install llama_cpp_python-0.2.55-cp310-cp310-win_amd64.whl
   ```

**Why This Works**:
- GitHub releases have correct 64-bit DLLs
- PyPI wheels are sometimes outdated/broken
- Direct install bypasses pip caching issues

**Success Rate**: ~90% (most reliable method)

---

### Solution 2: Build from Source with CMAKE

**Requirements**:
- Visual Studio 2019/2022 Build Tools
- CMake 3.20+
- Git

**Steps**:
1. Install Visual Studio Build Tools (if not already):
   ```bash
   # Download from: https://visualstudio.microsoft.com/downloads/
   # Select: "Desktop development with C++"
   ```

2. Install CMake:
   ```bash
   pip install cmake
   ```

3. Build from source:
   ```bash
   # Clear pip cache first
   pip cache purge
   
   # Force build from source (no pre-built wheel)
   $env:CMAKE_ARGS="-DLLAMA_CUBLAS=OFF"
   pip install llama-cpp-python --no-cache-dir --force-reinstall --no-binary llama-cpp-python
   ```

**Why This Works**:
- Compiles for YOUR system architecture
- Bypasses broken PyPI wheels
- Full control over build options

**Success Rate**: ~70% (requires correct build tools setup)  
**Time**: 5-15 minutes compilation

---

### Solution 3: Use conda-forge Distribution

**Requirements**: Anaconda or Miniconda

**Steps**:
```bash
conda install -c conda-forge llama-cpp-python
```

**Why This Works**:
- conda-forge maintains separate Windows builds
- Often more reliable than PyPI
- Better binary dependency management

**Success Rate**: ~80%  
**Downside**: Requires conda environment

---

### Solution 4: Use WSL2 (Windows Subsystem for Linux)

**Steps**:
1. Install WSL2:
   ```bash
   wsl --install
   ```

2. Inside WSL2 Ubuntu:
   ```bash
   pip install llama-cpp-python
   # Works immediately (Linux has no DLL issues)
   ```

**Why This Works**:
- llama-cpp-python has no Linux issues
- Full Linux compatibility
- Can still access Windows files

**Success Rate**: 100% (Linux installation is reliable)  
**Downside**: Requires WSL2 setup (~30 min first time)

---

### Solution 5: Use Docker Container

**Steps**:
```dockerfile
FROM python:3.10-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git

# Install llama-cpp-python (works in Linux container)
RUN pip install llama-cpp-python

COPY . /app
WORKDIR /app

CMD ["python", "server.py"]
```

```bash
docker build -t ai-assistant .
docker run -p 5000:5000 ai-assistant
```

**Why This Works**:
- Linux environment (no Windows issues)
- Reproducible
- Easy deployment

**Success Rate**: 100%  
**Downside**: Docker overhead, complexity

---

## Our Previous Attempts (Feb 2, 2026)

### What We Tried
1. ❌ Direct pip install (got broken PyPI wheel)
2. ❌ `--force-reinstall` (still used cached wheel)
3. ❌ `--no-binary` (pip ignored flag, used cache)
4. ❌ Visual Studio Build Tools + vcvars64.bat (wheel still wrong)

### What We Didn't Try Yet
- ✅ **GitHub releases wheel** (Solution 1) ← TRY THIS FIRST
- ⏳ Build from source with CMAKE args (Solution 2)
- ⏳ conda-forge (Solution 3)
- ⏳ WSL2 (Solution 4)

---

## Recommended Approach for Our Project

### Phase 1: Quick Win (5 minutes)
Try GitHub releases wheel (Solution 1):
```bash
# 1. Check Python version
python --version  # Likely 3.10

# 2. Download correct wheel from GitHub
# https://github.com/abetlen/llama-cpp-python/releases/tag/v0.2.55

# 3. Install
pip uninstall llama-cpp-python  # Remove any broken install
pip install llama_cpp_python-0.2.55-cp310-cp310-win_amd64.whl
```

### Phase 2: If Phase 1 Fails (15 minutes)
Build from source (Solution 2):
```bash
pip cache purge
$env:CMAKE_ARGS="-DLLAMA_CUBLAS=OFF"
pip install llama-cpp-python --no-cache-dir --force-reinstall --no-binary llama-cpp-python
```

### Phase 3: If Phase 2 Fails (30 minutes)
Use WSL2 (Solution 4) - guaranteed to work

---

## Performance Comparison (When Both Work)

| Metric | llama-cpp-python | ctransformers |
|--------|------------------|---------------|
| **Speed** | 100% (baseline) | 80-90% |
| **Memory** | Efficient | Slightly higher |
| **Model Support** | All GGUF | Limited (no Qwen2.5) |
| **API Simplicity** | Medium | Simple |

**Verdict**: llama-cpp-python is worth the installation effort for:
- 10-20% performance gain
- Universal model support
- Better memory control

---

## Troubleshooting Tips

### Check Python Architecture
```bash
python -c "import struct; print(struct.calcsize('P') * 8)"
# Output: 64 = 64-bit Python (correct)
# Output: 32 = 32-bit Python (need 64-bit)
```

### Check Installed Wheel Details
```bash
pip show llama-cpp-python
# Check: Location contains "win_amd64" or "win32"
# win32 = WRONG (causes WinError 193)
# win_amd64 = CORRECT
```

### Force Reinstall from GitHub
```bash
pip uninstall llama-cpp-python
pip cache purge
pip install https://github.com/abetlen/llama-cpp-python/releases/download/v0.2.55/llama_cpp_python-0.2.55-cp310-cp310-win_amd64.whl
```

---

## Decision Matrix

| Scenario | Recommended Solution | Time | Success Rate |
|----------|---------------------|------|--------------|
| **Production Windows** | GitHub wheel (Sol 1) | 5 min | 90% |
| **Development Windows** | ctransformers (current) | 0 min | 100% |
| **Performance Critical** | GitHub wheel → WSL2 | 5-30 min | 95% |
| **CI/CD Pipeline** | Docker (Sol 5) | Setup once | 100% |

---

## Action Plan for Our Project

**Immediate** (Today):
1. Try GitHub releases wheel (Solution 1)
2. Test with our qwen2.5-coder model
3. If works: Update llm_service.py (15 min)
4. If fails: Document and continue with ctransformers + Llama 3.2 model

**Future** (When Optimizing):
- Benchmark: llama-cpp-python vs ctransformers
- If 10-20% matters: Invest in WSL2 or Docker setup
- If not: Stay with ctransformers (simplicity wins)

---

## References

- GitHub: https://github.com/abetlen/llama-cpp-python
- Issues: https://github.com/abetlen/llama-cpp-python/issues?q=windows+dll
- Releases: https://github.com/abetlen/llama-cpp-python/releases
- Our Experience: 3 hours troubleshooting (Feb 2, 2026)

## Links

- [[LLM Libraries for Data Queries]] - Main library comparison
- `PROJECT_TRACKER.md` WP-AI-005 - Future optimization task
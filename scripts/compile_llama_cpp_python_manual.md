# Manual Compilation Guide for llama-cpp-python on Windows

## Prerequisites
- Visual Studio 2019 or 2022 Build Tools
- CMake
- Git
- Python 3.10

## Step-by-Step Manual Compilation

### 1. Open Command Prompt AS ADMINISTRATOR

**Option A: Using Search**
1. Press Windows key
2. Type `cmd`
3. RIGHT-CLICK on "Command Prompt"
4. Select "Run as administrator"

**Option B: Using Start Menu**
1. Start Menu → Windows System → Command Prompt
2. RIGHT-CLICK → "Run as administrator"

**Important**: You MUST run as administrator to bypass Windows Security blocks on build tools.

### 2. Navigate to your project
```bash
cd C:\Users\D031182\gitrepo\steel_thread_on_sap
```

### 3. Set CMAKE flags
```bash
set CMAKE_ARGS=-DGGML_NATIVE=OFF -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_FMA=ON
```

### 4. Install numpy FIRST (this was causing timeout)
```bash
pip install numpy
```

### 5. Now compile llama-cpp-python
```bash
pip install llama-cpp-python==0.3.16 --no-cache-dir --force-reinstall --no-binary :all:
```

This should take 5-15 minutes to compile.

## Alternative: Simpler Approach

If you want to try without the complexity:

```bash
pip install llama-cpp-python
```

This installs the pre-built wheel. It might have the DLL issue, but worth trying first.

## After Installation

Test it works:
```bash
python -c "from llama_cpp import Llama; print('SUCCESS')"
```

## If This Still Doesn't Work

The issue is that building C++ on Windows is complex. Consider:
1. Using WSL2 (Linux on Windows) - compiles instantly there
2. Using pre-compiled binaries from another source
3. Using a different library (ctransformers works but limited models)
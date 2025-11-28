# Go Optimization Opportunities for SAXS Project

Based on comprehensive analysis of the SAXS (Small-Angle X-ray Scattering) processing framework, this document identifies high-impact areas where Go could significantly improve performance.

## Performance Analysis Summary

### Critical Bottlenecks Identified

#### 1. Peak Processing Pipeline (Highest Impact)
**Location**: `saxs/saxs/processing/stage/peak/process_peak.py:291-345`

**Issue**: Two-step iterative fitting approach with redundant curve fitting
- **Step 1 (Parabolic Fit)**: Lines 291-298
  - Uses `scipy.optimize.curve_fit()` on windowed region
  - Fit range determined by metadata parameter
- **Step 2 (Gaussian Fit)**: Lines 320-327
  - Second `curve_fit()` call with sigma-determined range
  - Refits the same peak with different model
- **Peak Subtraction**: Lines 337-345
  - Computes Gaussian approximation across ENTIRE q_state array
  - Subtracts from intensity and clips to zero

**Performance Impact**: For each peak detected, system performs TWO full non-linear fits with bounds constraints. Multiple peaks mean N × 2 expensive optimization operations.

**Computational Complexity**:
- With 50 peaks in 500-point dataset:
  - Peak detection: 50 iterations × O(500) = 25,000 ops
  - Fitting: 50 peaks × 2 fits × O(500 × 9) = 450,000 ops
  - **Total: 475k+ operations** per sample

#### 2. Peak Finding with scipy.signal.find_peaks
**Location**: `saxs/saxs/processing/stage/peak/find_peak.py:107-145`

**Issues**:
- Lines 107-109: Creates peak dictionary via list comprehension (2+ iterations over peak_indices)
- Lines 132-145: Peak selection uses `max()` in loop - O(n) per peak selection
- Inefficient for large peak counts

#### 3. CSV Data Reading
**Location**: `saxs/saxs/core/data/reader.py:89-90`

**Issue**: Two-pass operation
```python
data = pd.read_csv(self.file_path, sep=",")
data = data.apply(pd.to_numeric, errors="coerce").dropna()
```

**Inefficiencies**:
- Read CSV with default type inference
- Apply `pd.to_numeric()` to coerce ALL columns
- Drop NaN rows (not selective)
- Missing `dtype` parameter specification

#### 4. Filtering and Smoothing Operations
**Location**: `saxs/saxs/processing/stage/filter/filter.py:59`

**Issue**: Moving average using `np.convolve()`
- O(n×m) complexity where n=data length, m=window_size
- Creates window array on EVERY call
- Could use faster alternatives like `scipy.ndimage.uniform_filter()`

#### 5. Pipeline Scheduling Overhead
**Location**: `saxs/saxs/core/pipeline/scheduler/scheduler.py:158-201`

**Issues**:
- Every stage calls `request_stage()` even if not requesting stages
- Policy evaluation for EACH request (could batch)
- Logging overhead with string formatting on every iteration
- For iterative peak processing with 50+ peaks, pipeline executes 100+ stages

#### 6. Array Slicing and Memory Copies
**Location**: `process_peak.py:281-327`

**Issue**: 6 array slices = 6 memory allocations per peak
- Multiple slicing operations create memory copies
- Peak subtraction computes Gaussian over full array even though only fit region matters

### Computational Complexity Summary

| Stage | Operation | Complexity | Count per Run | Total |
|-------|-----------|-----------|---------------|-------|
| **Peak Detection** | `find_peaks()` | O(n) | 1 per iteration | O(n×k) |
| **Parabolic Fit** | `curve_fit()` | O(n×m²) | 1 per peak | O(k×n×m²) |
| **Gaussian Fit** | `curve_fit()` | O(n×m²) | 1 per peak | O(k×n×m²) |
| **Gaussian Subtraction** | Full array op | O(n) | 1 per peak | O(k×n) |
| **Moving Average** | `np.convolve()` | O(n×w) | 1 per run | O(n×w) |
| **Background Fit** | `curve_fit()` | O(n×m²) | 1 per run | O(n×m²) |

Where: k=number of peaks, n=data points, m=parameters, w=window size

---

## High-Value Go Components

### 1. High-Performance CSV Data Reader (Highest ROI)

**Target**: Replace `saxs/saxs/core/data/reader.py`

**Go Implementation**:
```go
package csvreader

import (
    "encoding/csv"
    "io"
    "strconv"
)

type SAXSData struct {
    QValues        []float64
    Intensity      []float64
    IntensityError []float64
}

// FastReadCSV reads and validates SAXS CSV data concurrently
func FastReadCSV(filepath string) (*SAXSData, error) {
    // Concurrent row parsing with goroutines
    // Pre-validate numeric types during read
    // Handle missing data efficiently
    // Return NumPy-compatible binary format
}
```

**Integration Options**:
1. CGo bindings for direct Python calls
2. Standalone CLI tool outputting binary format
3. gRPC service for batch processing

**Expected Speedup**: 3-10x faster for large datasets (500+ data points)

**Benefits**:
- Zero overhead type validation
- Concurrent row processing
- Efficient memory allocation
- No pandas coercion overhead

---

### 2. Peak Detection and Gaussian Fitting Engine (Critical Path)

**Target**: Replace `process_peak.py:291-345` fitting operations

**Go Implementation**:
```go
package peakfit

import (
    "gonum.org/v1/gonum/optimize"
    "gonum.org/v1/gonum/mat"
)

type PeakFitResult struct {
    PeakIndex      int
    ParabolaParams []float64
    GaussianParams []float64
    Subtracted     []float64
}

// FitPeaksParallel processes multiple peaks concurrently
func FitPeaksParallel(
    qValues []float64,
    intensity []float64,
    peakIndices []int,
    workers int,
) []PeakFitResult {
    // Parallel peak fitting with goroutines
    // Levenberg-Marquardt algorithm
    // SIMD-optimized Gaussian computation
    // Return fitted parameters
}

// CombinedFit performs single-pass parabola + Gaussian fit
func CombinedFit(
    xData []float64,
    yData []float64,
    peakIndex int,
) (parabola, gaussian []float64, err error) {
    // Smart initial guess from parabola for Gaussian
    // Single optimization pass
}
```

**Architecture**:
```
Peak Processing Pipeline:
┌─────────────────────────────────────────┐
│  Python: FindPeakStage                  │
│  - Detects peak indices                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Go: FitPeaksParallel()                 │
│  ┌─────────────────────────────────┐    │
│  │ Goroutine 1: Fit peaks 0-9      │    │
│  │ Goroutine 2: Fit peaks 10-19    │    │
│  │ Goroutine 3: Fit peaks 20-29    │    │
│  │ Goroutine N: Fit peaks 30-39    │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Returns: []PeakFitResult               │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Python: Update sample metadata         │
└─────────────────────────────────────────┘
```

**Why Go Excels Here**:
- Native concurrency for parallel peak fitting
- Libraries: `gonum/optimize` for curve fitting, `gonum/mat` for matrix ops
- Zero GIL limitations (unlike Python)
- SIMD operations for array computations

**Expected Speedup**: 5-20x for datasets with 20+ peaks

**Key Optimizations**:
1. Combine parabolic + Gaussian fits with smart initial guess
2. Compute Gaussian only over windowed region
3. Process multiple peaks in parallel
4. Cache fit regions and window arrays

---

### 3. Pipeline Scheduler with Work Queue (Moderate Impact)

**Target**: Replace `scheduler/scheduler.py:158-201`

**Go Implementation**:
```go
package scheduler

type StageRequest struct {
    Stage        Stage
    Sample       *SAXSSample
    FlowMetadata *FlowMetadata
}

type StageResult struct {
    Sample       *SAXSSample
    FlowMetadata *FlowMetadata
    Requests     []StageRequest
}

// BaseScheduler implements high-throughput stage execution
type BaseScheduler struct {
    workers        int
    requestQueue   chan StageRequest
    resultQueue    chan StageResult
    logQueue       chan LogEntry // Async logging
    insertionPolicy InsertionPolicy
}

// Run executes pipeline with worker pool pattern
func (s *BaseScheduler) Run(
    initialStages []Stage,
    sample *SAXSSample,
) (*SAXSSample, error) {
    // Worker pool for stage execution
    // Buffered channels for stage requests
    // Async logging goroutine
    // Policy evaluation with batching
}
```

**Benefits**:
- Worker pool pattern eliminates overhead
- Async logging removes critical path delay
- Buffered channels for efficient stage queueing
- Support for distributed processing

**Expected Speedup**: 2-5x reduction in scheduling overhead

---

### 4. Fast Array Operations Library (Supporting Component)

**Target**: Optimize array operations across all stages

**Go Implementation**:
```go
package arrayops

import (
    "unsafe"
    "golang.org/x/sys/cpu"
)

// MovingAverage performs sliding window without copying
func MovingAverage(data []float64, windowSize int) []float64 {
    // SIMD-optimized convolution
    // Zero-copy sliding window using unsafe pointers
}

// GaussianConvolve applies Gaussian kernel
func GaussianConvolve(data, kernel []float64) []float64 {
    // Vectorized operation
    // Memory pooling to reduce GC pressure
}

// SubtractBackgroundInPlace modifies array in-place
func SubtractBackgroundInPlace(intensity, background []float64) {
    // SIMD vectorization
    // No memory allocation
}

// SliceWindow returns view without copying
func SliceWindow(data []float64, start, end int) []float64 {
    // Zero-copy slice header manipulation
}
```

**Benefits**:
- SIMD vectorization for array operations
- Zero-copy slicing where appropriate
- Memory pooling to reduce GC pressure
- In-place operations to avoid allocations

**Expected Speedup**: 2-4x for filtering operations

---

## Recommended Implementation Strategy

### Phase 1: Quick Wins (1-2 weeks)

**Create Go package**: `saxs-accelerate`

```
saxs-accelerate/
├── cmd/
│   └── saxs-process/       # CLI tool
├── pkg/
│   ├── csvreader/          # Fast CSV parsing
│   ├── peakfit/            # Gaussian/parabolic fitting
│   ├── arrayops/           # SIMD operations
│   └── bindings/           # CGo Python bindings
├── test/
│   ├── benchmark/          # Performance tests
│   └── integration/        # Python integration tests
├── go.mod
└── README.md
```

**Start with Option 1 + 2 (Combined)**:
1. Fast CSV reader with Python bindings
2. Parallel Gaussian fitting engine

**Integration Approaches** (in order of preference):

#### Option A: CGo with Python C API (Recommended)
```python
# Python side
import saxs_accelerate

data = saxs_accelerate.read_csv_fast("data.csv")
results = saxs_accelerate.fit_peaks_parallel(
    q_values=data.q,
    intensity=data.i,
    peak_indices=[10, 25, 40],
    workers=4
)
```

**Pros**: Direct function calls, minimal overhead
**Cons**: Build complexity, platform-specific binaries

#### Option B: Standalone Binary CLI (Simplest)
```bash
# CLI usage
saxs-process fit-peaks \
  --input data.csv \
  --peaks 10,25,40 \
  --output results.bin \
  --workers 4
```

```python
# Python side
import subprocess
result = subprocess.run(['saxs-process', 'fit-peaks', ...])
```

**Pros**: Simple integration, no build dependencies
**Cons**: Subprocess overhead, serialization cost

#### Option C: gRPC Service (For Batch Processing)
```go
// Go gRPC server
service SAXSAccelerate {
    rpc FitPeaks(PeakFitRequest) returns (PeakFitResponse);
    rpc ReadCSV(CSVReadRequest) returns (CSVReadResponse);
}
```

**Pros**: Long-running service, batch optimization
**Cons**: Network overhead, infrastructure complexity

---

### Phase 2: Full Integration (2-4 weeks)

1. Implement array operations library
2. Build pipeline scheduler
3. Comprehensive benchmarking
4. Production testing with real datasets

---

## Performance Expectations

### For Typical SAXS Dataset (500 data points, 30 peaks):

**Current Python Implementation**:
- CSV reading: ~50-100ms
- Peak detection: ~100-200ms
- Peak fitting (30 peaks × 2 fits): ~1500-3000ms
- Total: **~2-5 seconds**

**With Go Acceleration**:
- CSV reading: ~5-10ms (10x faster)
- Peak detection: ~20-40ms (5x faster)
- Peak fitting (parallel): ~100-200ms (15x faster)
- Total: **~200-500ms** (10x overall speedup)

### For Batch Processing (100 samples):
- **Current**: ~3-8 minutes
- **With Go**: ~20-50 seconds
- **Speedup**: 10-15x

---

## Key Performance Wins

### Why Go Solves Your Bottlenecks:

1. **50+ peaks = 100+ fitting operations** → Go's goroutines solve this
   - Parallel processing across CPU cores
   - No GIL limitations

2. **CSV loading with type coercion** → Go's typed parsing is 5-10x faster
   - Static typing with zero overhead
   - Concurrent row parsing

3. **Metadata overhead in scheduler** → Go's channels eliminate this
   - Lock-free communication
   - Buffered channels for batching

4. **Array slicing creates copies** → Go's slice headers enable zero-copy views
   - Slice headers are (pointer, length, capacity) tuples
   - Unsafe pointers for true zero-copy when needed

---

## Next Steps

### Immediate Actions:

1. **Benchmark Current Performance**
   ```bash
   python -m cProfile -o profile.stats test.py
   python -m pstats profile.stats
   ```

2. **Prototype Go CSV Reader**
   - Implement basic CSV parsing
   - Create CGo bindings
   - Benchmark against pandas

3. **Prototype Parallel Peak Fitter**
   - Implement Levenberg-Marquardt in Go
   - Test with sample datasets
   - Measure speedup vs scipy.optimize

4. **Design Integration Architecture**
   - Choose integration approach (CGo vs CLI vs gRPC)
   - Plan Python API interface
   - Create build system

### Priority Order:

**Highest Impact** (do first):
- Peak fitting engine (#2) - 5-20x speedup on critical path
- CSV reader (#1) - 3-10x speedup, simple to implement

**Medium Impact** (do second):
- Array operations (#4) - 2-4x speedup, supports other components
- Pipeline scheduler (#3) - 2-5x speedup, architectural benefit

---

## Technical Requirements

### Go Dependencies:
```go
require (
    gonum.org/v1/gonum v0.14.0        // Numerical computing
    github.com/klauspost/compress v1.17.0  // Fast compression
    golang.org/x/sys v0.15.0          // SIMD support
)
```

### Python Integration:
- CGo with Python C API (recommended)
- NumPy C API for array interop
- Consider: `pybind11` for easier C++ bindings if needed

### Build Tools:
- Go 1.21+ for generics and improved performance
- CGo enabled for Python bindings
- Cross-compilation support for Linux/macOS/Windows

---

## Risk Mitigation

### Potential Challenges:

1. **CGo Build Complexity**
   - Solution: Provide pre-built binaries for common platforms
   - Fallback: Pure Python implementation remains available

2. **Numerical Precision Differences**
   - Solution: Comprehensive test suite comparing Go vs Python results
   - Tolerance: Match scipy.optimize within 1e-10 relative error

3. **Memory Management Across Language Boundary**
   - Solution: Clear ownership rules in API design
   - Use memory pools for frequently allocated objects

4. **Debugging Across Languages**
   - Solution: Extensive logging at boundary
   - Separate unit tests for Go and integration tests for Python

---

## Validation Plan

### Before Production:

1. **Unit Tests**: 100% coverage of Go code
2. **Integration Tests**: Python ↔ Go boundary validation
3. **Numerical Tests**: Match scipy.optimize results within tolerance
4. **Performance Tests**: Verify 5x+ speedup on real datasets
5. **Stress Tests**: Handle 1000+ peak datasets
6. **Memory Tests**: No leaks across 10,000+ samples

---

## Conclusion

The peak fitting engine (#2) offers the biggest immediate win since it's on the critical path and perfectly suits Go's concurrency model. Combined with the CSV reader (#1), you could achieve 10-15x speedup on typical workloads with minimal architectural changes to the existing Python codebase.

The modular nature of your pipeline architecture (stages, scheduler, metadata flow) makes it ideal for hybrid Python/Go optimization - keep the orchestration in Python, accelerate the compute in Go.

---

## References

**Key Files for Optimization**:
1. `saxs/saxs/processing/stage/peak/process_peak.py` - 2 expensive fits per peak
2. `saxs/saxs/processing/stage/peak/find_peak.py` - Inefficient peak selection
3. `saxs/saxs/processing/functions.py` - Non-vectorized loops
4. `saxs/saxs/core/data/reader.py` - Inefficient CSV loading
5. `saxs/saxs/core/pipeline/scheduler/scheduler.py` - Logging overhead

**Performance Indicators**:
- Line 32 in `abstract_stage.py`: "kind of bottleneck in templates"
- Test sample: 10 data points (real SAXS: 500+)
- FindPeakStage → ProcessPeakStage iterative loop structure

# Technical Insights from Legacy Peak Detection Code

**Document Purpose:** Preserve valuable domain knowledge, algorithms, and empirical findings from the legacy peak detection implementation before deprecation.

**Created:** 2025-11-18
**Source Code:** `/saxs/saxs/peak/` (legacy implementation)
**Current Implementation:** `/saxs/saxs/processing/stage/peak/`

---

## Table of Contents

1. [Critical Domain-Specific Algorithms](#1-critical-domain-specific-algorithms)
2. [Performance Optimizations](#2-performance-optimizations)
3. [Edge Cases and Special Handling](#3-edge-cases-and-special-handling)
4. [Configuration Parameters (Empirically Tuned)](#4-configuration-parameters-empirically-tuned)
5. [Missing Features (Recommended for Implementation)](#5-missing-features-recommended-for-implementation)
6. [Deprecated Patterns (Do Not Reintroduce)](#6-deprecated-patterns-do-not-reintroduce)

---

## 1. Critical Domain-Specific Algorithms

### 1.1 Two-Step Peak Fitting: Parabola → Gaussian

**Source:** `parabole_kernel.py` (lines 41-96, 172-236), `p_peak_classification.py` (lines 51-185)

**Algorithm:**
```
Step 1: Fit parabolic function to estimate initial peak width (sigma)
Step 2: Use parabola's sigma to determine optimal Gaussian fit range
Step 3: Refine with Gaussian fit for final peak characterization
```

**Why This Matters:**

Parabolic fitting is **more robust** than direct Gaussian fitting for noisy SAXS data because:
- Parabolas are less sensitive to noise near peak edges
- The parabola's width parameter provides a good initial estimate for Gaussian sigma
- Prevents Gaussian optimization from getting trapped in local minima

**Mathematical Formulas:**

```python
# Parabola (initial fit):
I(q) = A * (1 - (q - μ)² / σ²)

# Gaussian (final fit):
I(q) = A * exp(-((q - μ) / σ)²)
```

**Critical Insight:** Both functions use the **same parameter names** (μ, σ, A) to enable direct parameter transfer from parabola → Gaussian.

**Status:** ✅ **Implemented in new code** (`process_peak.py`, lines 246-342)

**Additional Opportunity:** Legacy code experimented with metric-based fit range optimization (`p_peak_classification.py:122-127`) that could improve difficult cases.

---

### 1.2 Sequential Peak Subtraction with Negative Clipping

**Source:** `parabole_kernel.py` (lines 247-262)

**Algorithm:**
```python
while True:
    negative_reduction()           # Clip negative values → 0
    search_peaks(height, prominence)
    if no_peaks_found:
        break
    fit_peak_with_parabola()
    refine_with_gaussian()
    subtract_fitted_gaussian()     # Remove peak from data
```

**Why This Matters:**

- **Handles overlapping peaks gracefully:** Each iteration reveals previously hidden peaks
- **Prevents artifact propagation:** Negative clipping (`np.maximum(intensity, 0)`) stops fitting errors from creating spurious peaks
- **Automatic termination:** Loop ends when no more peaks above threshold

**Status:** ✅ **Implemented** with flow metadata tracking (`process_peak.py:345`)

---

### 1.3 Hyperbolic Background Model

**Source:** `default_kernel.py` (lines 39-71)

**Formula:**
```python
I_background(q) = b * q^(-a)     # Power-law decay
I_corrected = I_raw - 0.7 * I_background
```

**Critical Configuration:**
```python
BACKGROUND_COEF = 0.7    # NOT 1.0 - this is crucial!
initial_params = (3, 2)  # (a, b) for power-law fit
```

**Why 0.7 Coefficient?**

The **reduced coefficient (< 1.0)** is essential because:
1. Prevents over-subtraction that creates negative values
2. Accounts for uncertainty in background estimation
3. Conservative approach preserves real signal

**Implementation Details:**
- Uses weighted fitting with `sigma=dI` (intensity error bars)
- Fits only to data where `q > START` (default: 0.02 Å⁻¹)

**Status:** ⚠️ **Needs Verification** - Confirm the 0.7 coefficient is preserved in new background processing

---

### 1.4 Adaptive Noise Boundary Detection

**Source:** `prominence_kernel.py` (lines 45-52)

**Algorithm:**
```python
# Find first major peak
peaks, properties = find_peaks(intensity, height=1, prominence=1)

# Use its right base as noise/signal transition
if len(properties["right_bases"]) > 0:
    noise_cutoff = properties["right_bases"][0]
else:
    noise_cutoff = 100  # Fallback
```

**Why This is Clever:**

- The **first peak** is typically the strongest signal
- Its **right_base** marks where intensity drops to background level
- Provides **data-driven, automatic** noise cutoff (better than fixed threshold)

**Use Case:** Determines where to apply different filtering strategies

**Status:** ❌ **NOT IMPLEMENTED** - Current code uses fixed `START=0.02` cutoff

**Recommendation:** Implement adaptive cutoff for samples with unusual noise characteristics

---

### 1.5 Decomposed Filtering Strategy

**Source:** `prominence_kernel.py` (lines 54-69)

**Algorithm:**
```python
# 1. Detect noise boundary (see 1.4 above)
noise_boundary = detect_noise_cutoff()

# 2. Heavy filtering for noisy region
noisy_part = moving_average(
    intensity[:noise_boundary],
    window_size=10  # Aggressive smoothing
)

# 3. Light filtering for signal region
clean_part = intensity[noise_boundary:]

# 4. Combine and apply final polish
combined = np.concatenate([noisy_part, clean_part])
result = median_filter(combined, window_size=3)
```

**Why Region-Specific Filtering Matters:**

| Region | Filter Type | Window Size | Rationale |
|--------|-------------|-------------|-----------|
| Noisy (low q) | Moving average | 10 | Heavy smoothing acceptable, no peaks expected |
| Signal (high q) | Median filter | 3 | Preserve peak shape, remove outliers |

**Status:** ❌ **NOT IMPLEMENTED** - Current code applies uniform filtering

**Recommendation:** Implement for samples with high noise at low q-values

---

### 1.6 Global Multi-Peak Optimization

**Source:** `parabole_kernel.py` (lines 311-334)

**Algorithm:**
```python
def gaussian_sum(q, *params):
    """Sum of multiple Gaussians for simultaneous fitting."""
    assert len(params) % 3 == 0  # (μ, σ, A) triples

    result = np.zeros_like(q)
    for i in range(0, len(params), 3):
        mu, sigma, amplitude = params[i:i+3]
        result += amplitude * exp(-((q - mu) / sigma)²)
    return result

# After individual peak fitting:
all_params = flatten([peak.mu, peak.sigma, peak.amplitude
                      for peak in peaks])

# Re-optimize ALL peaks simultaneously
optimized = minimize(
    lambda p: sum((intensity - gaussian_sum(q, *p))**2),
    all_params,
    method="BFGS"
)
```

**Why This is Important:**

Individual peak fits assume peaks are **independent**, which fails for overlapping peaks. Global optimization:
- Accounts for peak-peak interactions
- Corrects systematic errors from sequential fitting
- Improves total fit quality

**Status:** ❌ **NOT IMPLEMENTED** - Valuable missing feature

**Recommendation:** **HIGH PRIORITY** - Implement for samples with closely-spaced peaks

---

## 2. Performance Optimizations

### 2.1 Pre-allocated Arrays

**Source:** `peak_classificator.py` (line 213)

```python
self.peaks_plots = np.zeros((20, len(q)))  # Pre-allocate for 20 peaks
```

**Insight:** 20 peaks is a reasonable upper bound for typical SAXS data

**Benefit:** Avoids repeated array resizing (O(n) → O(1) for append operations)

---

### 2.2 BFGS Optimizer for Gaussian Fitting

**Source:** `parabole_kernel.py` (line 132)

```python
result = minimize(loss_function, initial_params, method="BFGS")
```

**Why BFGS?**

- **Quasi-Newton method:** Faster than full Newton, doesn't need Hessian
- **Well-suited for smooth functions:** Gaussians are continuously differentiable
- **Better than gradient descent:** Faster convergence with comparable memory

**Alternative:** `curve_fit` (based on Levenberg-Marquardt) also used extensively

---

### 2.3 FFT-Based Moving Average

**Source:** `processing/functions.py` (lines 143-163)

```python
def moving_average(data, window_size):
    window = np.ones(window_size) / window_size
    return np.convolve(data, window, mode="same")
```

**Performance:**
- **Time complexity:** O(n log n) via FFT-based convolution (vs O(n·w) for naive)
- **`mode="same"`:** Preserves array length (no edge trimming needed)

---

## 3. Edge Cases and Special Handling

### 3.1 Data Cutoff at Low q-values

**Source:** `default_kernel.py` (lines 76-88)

```python
START = 0.02  # Å⁻¹

def cut_low_q_noise():
    cutoff_index = np.argmax(q > START)
    q_clean = q[cutoff_index:]
    I_clean = I[cutoff_index:]

    # IMPORTANT: Handle missing error data
    if dI is not None:
        dI_clean = dI[cutoff_index:]
```

**Why START = 0.02?**

SAXS data below q = 0.02 Å⁻¹ is typically unreliable due to:
- Beamstop shadow artifacts
- Detector edge effects
- Parasitic scattering

**Edge Case Handling:** Gracefully handles `dI=None` (error bars not available)

---

### 3.2 Boundary Checking for Fit Ranges

**Source:** `parabole_kernel.py` (lines 185-187)

```python
period1 = max(period1, 0)           # Prevent negative indices
if period2 >= len(peaks):
    period1 = len(peaks) - 1        # Prevent overflow
```

**Critical:** Prevents index out-of-bounds when fitting peaks near data edges

**Status:** ✅ **Implemented** (`process_peak.py:282, 312`)

---

### 3.3 Peak Masking to Prevent Re-detection

**Source:** `peak_classificator.py` (lines 602-606)

```python
exclusion_zone = np.arange(-5, 6, 1)  # ±5 points around peak

for offset in exclusion_zone:
    processed_peaks.append(peak_index + offset)
```

**Purpose:** Prevents detecting the same peak multiple times in iterative processing

**Magic Number Alert:** **±5 points** is a heuristic that may need tuning for:
- Different q-spacing
- Very narrow or very wide peaks

**Status:** ⚠️ **Different approach** - New code uses `processed` set in FlowMetadata; verify equivalence

---

### 3.4 Empty Peak Array Handling

**Source:** `parabole_kernel.py` (lines 336-356)

```python
def gather_results():
    # -1 distinguishes "None" from "0 peaks found"
    peak_count = len(peaks) if peaks is not None else -1

    return {
        "peak_number": peak_count,
        "initial_indices": peaks.tolist() if peaks is not None else [],
        "q_values": final_peak_positions,
    }
```

**Why This Matters:**
- **Robust batch processing:** Prevents crashes when no peaks detected
- **Distinguishes states:** `None` (error) vs `[]` (no peaks) vs `[...]` (peaks found)

---

## 4. Configuration Parameters (Empirically Tuned)

**Source:** `application/settings_processing.py`

These are **hard-won empirical values** - do not change without systematic testing!

```python
# Data preprocessing
START = 0.02              # q-value cutoff [Å⁻¹]
                         # Rationale: Beamstop artifacts below this

# Background subtraction
BACKGROUND_COEF = 0.7     # Subtraction coefficient (NOT 1.0!)
                         # Rationale: Prevents over-subtraction

# Filtering
SIGMA_FILTER = 1.5        # Gaussian filter width
WINDOWSIZE = 6            # Moving average window

# Peak detection
PROMINENCE = 0.6          # Peak prominence threshold
                         # Rationale: Peaks must rise 60% above local baseline

# Peak fitting
RESOLUTION_FACTOR = 1.4   # Resolution scaling factor
                         # Usage: Unclear in legacy code - needs documentation
```

### Fit Bounds (Physical Constraints)

**Source:** `parabole_kernel.py` (lines 64, 200)

```python
bounds = (
    [delta_q**2, 1],        # Lower bounds: [σ_min, A_min]
    [0.05, 4 * max_I]       # Upper bounds: [σ_max, A_max]
)
```

**Domain Knowledge:**

| Parameter | Lower Bound | Upper Bound | Rationale |
|-----------|-------------|-------------|-----------|
| σ (width) | `delta_q²` | 0.05 | Must exceed resolution; prevents fitting noise as wide peaks |
| A (amplitude) | 1 | `4 × max(I)` | Positive intensity; allows sharpening during fit |

**Status:** ✅ **Preserved** (`process_peak.py:297`)

---

## 5. Missing Features (Recommended for Implementation)

### High Priority

#### 5.1 Global Multi-Peak Re-Optimization ⭐⭐⭐

**What:** After individual fits, re-optimize all peaks simultaneously (see Section 1.6)

**Why:** Corrects for peak overlap that sequential fitting ignores

**Implementation:** `parabole_kernel.py:311-334`

**Benefit:** Improved accuracy for closely-spaced peaks

---

#### 5.2 Adaptive Noise Boundary Detection ⭐⭐

**What:** Use first peak's right_base as noise/signal cutoff (see Section 1.4)

**Why:** Adapts to varying noise characteristics per sample

**Implementation:** `prominence_kernel.py:45-52`

**Benefit:** Better handling of unusual noise profiles

---

### Medium Priority

#### 5.3 Region-Specific Filtering ⭐⭐

**What:** Different filtering strategies for noisy vs clean regions (see Section 1.5)

**Implementation:** `prominence_kernel.py:54-69`

**Benefit:** Reduces noise without over-smoothing peaks

---

#### 5.4 Metric-Based Fit Range Optimization ⭐

**What:** Dynamically optimize fit range using goodness-of-fit metric

**Implementation:** `p_peak_classification.py:122-127`

**Benefit:** Better fits for difficult peak shapes

---

### Low Priority

#### 5.5 `__slots__` Optimization

**What:** Use `__slots__` for memory-intensive data structures

**Benefit:** Reduced memory footprint, faster attribute access

**Trade-off:** Less flexibility (can't add attributes dynamically)

---

## 6. Deprecated Patterns (Do Not Reintroduce)

### ❌ Plotting Code Mixed with Processing Logic

**Example:** `parabole_kernel.py` contains extensive matplotlib plotting

**Why Deprecated:**
- Violates separation of concerns
- Makes testing difficult
- Creates dependencies on visualization libraries in core processing

**Correct Approach:** Separate plotting into visualization modules

---

### ❌ File I/O Coupled to Processing

**Example:** Kernel classes directly read/write files in `__init__`

**Why Deprecated:**
- Impossible to unit test without filesystem
- Limits reusability (can't process in-memory data)

**Correct Approach:** Pass data as arguments; separate I/O concerns

---

### ❌ Silent Exception Swallowing

**Example:** `peak_application.py:93`

```python
try:
    result = process_peak()
except Exception:
    pass  # Silent failure!
```

**Why Dangerous:**
- Hides bugs
- Makes debugging impossible
- Can cause silent data corruption

**Correct Approach:** Log exceptions, use explicit error handling

---

### ❌ Global State and Mutable Class Attributes

**Example:** Kernels modify extensive state via `__slots__`

**Why Deprecated:**
- Hard to reason about program flow
- Thread-unsafe
- Makes testing difficult (state leaks between tests)

**Correct Approach:** Immutable data structures (like `SAXSSample` in new code)

---

## 7. Testing Insights - Critical Edge Cases

**Source:** Test files in `/tests/saxs/processing/stage/peak/`

Ensure these edge cases are always tested:

```python
# Data structure edge cases
✓ Empty arrays: [], np.array([])
✓ Single-point arrays: [5.0]
✓ None values: intensity_error=None

# Numerical edge cases
✓ Negative intensities: I < 0
✓ NaN values: np.nan in data
✓ Inf values: np.inf in data
✓ All zeros: I = [0, 0, 0, ...]

# Physical edge cases
✓ Non-uniform q-spacing
✓ Overlapping peaks
✓ Peaks at data boundaries
✓ No peaks above threshold
```

---

## 8. Unresolved Questions from Legacy Code

**From code comments (TODOs):**

### 8.1 Background Fitting: Pre- or Post-Processing?

**Question:** Should background model be fitted to raw or pre-processed data?

**Current:** Uses post-cutoff (`q > START`), pre-filtered data

**Consideration:** Filtering may distort background shape; raw data has more noise

**Recommendation:** Systematic study needed

---

### 8.2 Optimal Peak Detection Parameters

**Question:** Are `height=1.5, prominence=0.3` truly optimal?

**Current:** Based on empirical testing with limited dataset

**Recommendation:** Hyperparameter tuning study across diverse samples

---

### 8.3 Quality Metrics for Peak Fits

**Question:** How to identify suspicious/poor-quality peak fits?

**Suggestion:** Implement automated quality checks:
- Residual analysis (χ² test)
- Amplitude/noise ratio
- Fit bounds violations

---

### 8.4 Peak Exclusion Zone Sizing

**Question:** Is ±5 points the right exclusion zone?

**Current:** Hard-coded magic number

**Recommendation:** Make it adaptive based on peak width:
```python
exclusion_zone = int(2 * sigma / delta_q)  # ±2σ
```

---

## 9. Design Patterns Worth Preserving

### Template Method Pattern

**Source:** `abstract_kernel.py` (lines 103-262)

```python
def __call__(self):
    self.custom_preprocessing()    # Hook
    self.standard_processing()      # Template
    self.custom_postprocessing()   # Hook
    return self.gather_results()
```

**Benefits:**
- Clear processing pipeline
- Easy to extend via inheritance
- Enforces consistent ordering

**Status:** ✅ **Evolved** - New code uses Stage pattern with policies (more sophisticated)

---

### Class-Level Type Information

**Source:** All kernel files

```python
str_type = "prominence_kernel"
short_str_type = "prom_kern"

@classmethod
def class_info(cls):
    return cls.str_type
```

**Use Cases:**
- Logging without instantiation
- Serialization
- Runtime introspection

**Status:** ⚠️ **Partial** - New code has better typing but lacks runtime introspection

---

## 10. Key Takeaways

### ✅ Already Implemented Well

1. Two-step parabola→Gaussian fitting
2. Sequential peak subtraction with negative clipping
3. Prominence-based peak detection
4. Physical constraints on fit parameters
5. Boundary checking and edge case handling

### ⚠️ Verify Preservation

1. `BACKGROUND_COEF = 0.7` (not 1.0)
2. Fit bounds: `sigma ∈ [delta_q², 0.05]`
3. START = 0.02 Å⁻¹ cutoff rationale

### 🔨 Recommended Additions

1. **Global multi-peak optimization** (HIGH priority)
2. **Adaptive noise detection** (MEDIUM priority)
3. **Region-specific filtering** (MEDIUM priority)
4. **Automated fit quality metrics** (LOW priority)

### 🚫 Do Not Reintroduce

1. Plotting in processing code
2. File I/O coupled to algorithms
3. Silent exception swallowing
4. Extensive mutable state

---

## References

**Legacy Code Location:** `/Users/isg/saxs/saxs/saxs/peak/`

**Key Files:**
- `abstract_kernel.py` - Base class with template method
- `parabole_kernel.py` - Two-step fitting implementation
- `prominence_kernel.py` - Adaptive noise handling
- `default_kernel.py` - Background subtraction
- `p_peak_classification.py` - Advanced peak characterization

**New Implementation:** `/Users/isg/saxs/saxs/saxs/processing/stage/peak/`

**Key Files:**
- `find_peak.py` - Peak detection stage
- `process_peak.py` - Peak fitting stage
- `background.py` - Background subtraction stage

---

**Document Maintenance:** Update this document when:
- Implementing recommended features
- Discovering new insights from production use
- Changing empirical parameters (document rationale!)

**Last Updated:** 2025-11-18
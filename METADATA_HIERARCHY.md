# SAXS Metadata Type Hierarchy

**Purpose:** Documents the different metadata types used throughout the SAXS pipeline and their relationships.

**Created:** 2025-11-18

---

## Overview

The SAXS framework uses multiple metadata types to pass information between stages, track processing state, and make runtime decisions. This document clarifies the purpose and flow of each type.

---

## Metadata Type Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    METADATA TYPE HIERARCHY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Sample-Level Metadata                                       │
│     └─ SampleMetadata (attached to SAXSSample)                  │
│         Purpose: Domain-specific data about the sample          │
│         Examples: experiment_id, temperature, sample_name       │
│                                                                  │
│  2. Flow Metadata (Inter-Stage Communication)                   │
│     └─ FlowMetadata                                             │
│         Purpose: Pass processing state between stages           │
│         Examples: UNPROCESSED (peaks), CURRENT (peak)           │
│         Flow: Stage A → FlowMetadata → Stage B                  │
│                                                                  │
│  3. Stage Configuration Metadata                                │
│     ├─ CutStageMetadata                                         │
│     ├─ BackgroundStageMetadata                                  │
│     ├─ FilterStageMetadata                                      │
│     ├─ PeakFindStageMetadata                                    │
│     └─ PeakProcessStageMetadata                                 │
│         Purpose: Configure stage behavior (parameters)          │
│         Examples: cut_point, prominence, background_coef        │
│                                                                  │
│  4. Evaluation Metadata (Condition Logic)                       │
│     └─ EvalMetadata (extends FlowMetadata)                      │
│         Purpose: Data for condition evaluation                  │
│         Examples: CURRENT peak for ChainingPeakCondition        │
│         Flow: Stage → EvalMetadata → Condition.evaluate()       │
│                                                                  │
│  5. Approval Metadata (Scheduler Decisions)                     │
│     └─ ApprovalMetadata                                         │
│         Purpose: Additional data for scheduler insertion policy │
│         Examples: priority, constraints                         │
│         Flow: Policy → ApprovalMetadata → Scheduler             │
│                                                                  │
│  6. Scheduler Metadata (Runtime State)                          │
│     └─ SchedulerMetadata                                        │
│         Purpose: Track scheduler state and constants            │
│         Examples: ERuntimeConstants.UNDEFINED_PEAK              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Metadata Flow Through Pipeline

### Typical Processing Flow:

```
1. SAXSSample (with SampleMetadata)
   │
   ├─→ Stage A Configuration (e.g., CutStageMetadata)
   │   └─→ process(sample) → modified sample
   │
   ├─→ Stage A creates FlowMetadata
   │   └─→ {UNPROCESSED: {peak_data}}
   │
   └─→ Stage A (if IAbstractRequestingStage)
       │
       ├─→ create_request(flow_metadata) → StageRequest
       │   └─→ Contains: EvalMetadata + FlowMetadata
       │
       ├─→ ChainingPolicy.request(StageRequest)
       │   └─→ Condition.evaluate(EvalMetadata) → bool
       │
       └─→ StageApprovalRequest (if condition passes)
           └─→ Contains: Stage + ApprovalMetadata
```

---

## Detailed Metadata Types

### 1. SampleMetadata

**File:** `saxs/saxs/core/types/sample_objects.py`

**Purpose:** Domain-specific information about the physical sample being measured.

**Keys (`ESampleMetadataKeys`):**
- `EXPERIMENT_ID`: Unique identifier for experiment
- `SAMPLE_NAME`: Human-readable sample name
- `TEMPERATURE`: Measurement temperature
- `CONCENTRATION`: Sample concentration
- Custom keys as needed

**Usage:**
```python
sample.set_metadata(ESampleMetadataKeys.EXPERIMENT_ID, "EXP-2025-001")
experiment_id = sample.get_metadata()[ESampleMetadataKeys.EXPERIMENT_ID]
```

**Lifetime:** Attached to `SAXSSample` throughout entire pipeline.

---

### 2. FlowMetadata

**File:** `saxs/saxs/core/types/flow_metadata.py`

**Purpose:** Pass processing state and intermediate results between stages.

**Keys (`FlowMetadataKeys`):**
- `UNPROCESSED`: Set of unprocessed peaks (dict mapping index → intensity)
- `CURRENT`: Currently selected peak for processing
- `PROCESSED`: Set of already processed peaks
- Custom keys as needed

**Usage:**
```python
# Stage A sets flow metadata
flow_metadata[FlowMetadataKeys.UNPROCESSED] = peak_dict

# Stage B reads flow metadata
current_peak = flow_metadata[FlowMetadataKeys.CURRENT]
```

**Lifetime:** Created by stages, passed to next stage via scheduler.

**Key Insight:** FlowMetadata enables stateful processing without modifying the sample itself.

---

### 3. Stage Configuration Metadata

**Files:**
- `saxs/saxs/processing/stage/cut/types.py`
- `saxs/saxs/processing/stage/background/types.py`
- `saxs/saxs/processing/stage/peak/types.py`
- etc.

**Purpose:** Configure stage-specific behavior and parameters.

**Pattern:**
Each stage defines:
1. `E*MetadataKeys` (enum of keys)
2. `*StageMetadataDict` (TypedDict schema)
3. `*StageMetadata` (TAbstractStageMetadata wrapper)

**Example (CutStageMetadata):**
```python
class ECutMetadataKeys(EMetadataSchemaKeys):
    CUT_POINT = "cut_point"

class CutStageMetadataDict(MetadataSchemaDict, total=False):
    cut_point: int

class CutStageMetadata(TAbstractStageMetadata[...]):
    # Type-safe wrapper
```

**Usage:**
```python
cut_metadata = CutStageMetadata(value={"cut_point": 100})
cut_stage = CutStage(metadata=cut_metadata)
```

**Lifetime:** Set at stage initialization, immutable during processing.

---

### 4. EvalMetadata

**File:** `saxs/saxs/core/stage/request/abst_request.py`

**Purpose:** Subset of FlowMetadata used specifically for condition evaluation.

**Relationship:** Extends `FlowMetadata` (same keys, different semantic purpose).

**Usage:**
```python
# In FindPeakStage.create_request():
eval_metadata = EvalMetadata({
    FlowMetadataKeys.CURRENT.value: current_peak
})

# In ChainingPeakCondition.evaluate():
current = eval_metadata[EvalMetadata.Keys.CURRENT]
return current is not ERuntimeConstants.UNDEFINED_PEAK
```

**Why Separate Type?**
- Semantic clarity: "This data is for condition evaluation"
- Type safety: Ensures conditions receive expected data structure
- Future extensibility: Can add eval-specific methods

---

### 5. ApprovalMetadata

**File:** `saxs/saxs/core/pipeline/scheduler/abstract_stage_request.py`

**Purpose:** Additional information for scheduler's insertion policy to make decisions.

**Keys:** Currently minimal (typically empty dict), extensible for future use.

**Potential Future Uses:**
- Priority level for stage insertion
- Resource requirements
- Timing constraints
- Dependencies on other stages

**Usage:**
```python
approval = ApprovalMetadata(value={})
approval_request = StageApprovalRequest(
    stage=peak_process_stage,
    approval_metadata=approval
)
```

**Lifetime:** Created by chaining policy, consumed by scheduler.

---

### 6. SchedulerMetadata

**File:** `saxs/saxs/core/types/scheduler_metadata.py`

**Purpose:** Scheduler-level state and runtime constants.

**Contains:**
- `ERuntimeConstants`: Sentinel values (e.g., `UNDEFINED_PEAK = -1`)

**Usage:**
```python
if current_peak == ERuntimeConstants.UNDEFINED_PEAK:
    # No more peaks to process
    return empty_request()
```

---

## Metadata Lifecycle Example

Let's trace metadata through a complete peak processing workflow:

### Initial State

```python
# 1. Sample with metadata
sample = SAXSSample(
    q_values=q,
    intensity=I,
    metadata=SampleMetadata({
        ESampleMetadataKeys.EXPERIMENT_ID: "EXP-001"
    })
)
```

### Stage 1: CutStage

```python
# 2. Cut stage with configuration metadata
cut_stage = CutStage(
    metadata=CutStageMetadata(value={"cut_point": 100})
)

# 3. Process sample
sample = cut_stage.process(sample)
# Sample is truncated, but SampleMetadata unchanged
```

### Stage 2: FindPeakStage

```python
# 4. Find peaks
find_peak_stage = FindPeakStage(...)
sample = find_peak_stage.process(sample)

# 5. Stage creates FlowMetadata
flow_metadata = FlowMetadata({
    FlowMetadataKeys.UNPROCESSED: {
        150: 45.2,  # index: intensity
        200: 38.1,
        250: 42.7
    }
})

# 6. Create request with EvalMetadata
eval_metadata = EvalMetadata({
    FlowMetadataKeys.CURRENT: {150: 45.2}  # Selected peak
})

request = StageRequest(
    condition_eval_metadata=eval_metadata,
    flow_metadata=flow_metadata
)
```

### Stage 3: Condition Evaluation

```python
# 7. Chaining policy evaluates condition
policy = SingleStageChainingPolicy(
    condition=ChainingPeakCondition(),
    pending_stages=[ProcessPeakStage()]
)

# 8. Condition checks EvalMetadata
result = condition.evaluate(eval_metadata)
# Returns: True (CURRENT is not UNDEFINED_PEAK)
```

### Stage 4: Approval Request

```python
# 9. Policy creates approval request
if result:
    approval = StageApprovalRequest(
        stage=ProcessPeakStage(),
        approval_metadata=ApprovalMetadata(value={})
    )
```

### Stage 5: Scheduler Insertion

```python
# 10. Scheduler decides based on insertion policy
scheduler.handle_stage_request(approval)
# Enqueues ProcessPeakStage with FlowMetadata
```

---

## Design Rationale

### Why So Many Metadata Types?

Each type serves a distinct purpose in the separation of concerns:

| Type | Purpose | Owner | Lifetime |
|------|---------|-------|----------|
| SampleMetadata | Domain data | Sample | Entire pipeline |
| FlowMetadata | Inter-stage state | Stages | Stage-to-stage |
| StageMetadata | Configuration | Stage | Stage initialization |
| EvalMetadata | Condition logic | Requesting stage | Single evaluation |
| ApprovalMetadata | Scheduler decisions | Chaining policy | Single request |
| SchedulerMetadata | Runtime constants | Framework | Static |

### Benefits

1. **Type Safety:** Each type has specific structure and validation
2. **Clear Ownership:** Who creates, modifies, and consumes each type
3. **Loose Coupling:** Stages don't depend on each other's internals
4. **Testability:** Each metadata type can be mocked independently
5. **Extensibility:** New keys can be added without breaking existing code

### Drawbacks (Acknowledged)

1. **Complexity:** 6 different types to understand
2. **Cognitive Overhead:** Must know which type to use when
3. **Potential Overlap:** EvalMetadata vs FlowMetadata distinction is subtle

---

## Simplification Opportunities

### Potential Consolidation

If complexity becomes problematic, consider:

1. **Merge EvalMetadata into FlowMetadata**
   - Keep same dict, just use FlowMetadata type
   - Lose semantic distinction but reduce types

2. **Merge ApprovalMetadata into StageApprovalRequest**
   - Inline the dict into the request class
   - Only useful if ApprovalMetadata remains minimal

3. **Create MetadataRegistry**
   - Single registry with typed accessors
   - `registry.get_flow_data()`, `registry.get_stage_config()`, etc.

### Recommendation

**Keep current structure** because:
- Type safety benefits outweigh complexity
- Clear separation aids debugging
- Each type has distinct lifecycle and purpose
- Production systems benefit from explicit types

---

## Best Practices

### When Creating Metadata

1. **SampleMetadata**: Physical properties of the sample
   ```python
   sample.set_metadata(ESampleMetadataKeys.TEMPERATURE, 298.15)
   ```

2. **FlowMetadata**: Processing state to pass to next stage
   ```python
   flow = FlowMetadata({FlowMetadataKeys.UNPROCESSED: peaks})
   ```

3. **StageMetadata**: Configuration at stage creation
   ```python
   metadata = CutStageMetadata(value={"cut_point": config.cut})
   ```

### When Reading Metadata

1. Always use enum keys (not string literals)
   ```python
   # ✅ GOOD
   value = metadata[FlowMetadataKeys.CURRENT]

   # ❌ BAD
   value = metadata["current"]
   ```

2. Check for key existence before access
   ```python
   if FlowMetadataKeys.CURRENT in flow_metadata:
       current = flow_metadata[FlowMetadataKeys.CURRENT]
   ```

3. Use type hints for clarity
   ```python
   def process_flow(metadata: FlowMetadata) -> SAXSSample:
       # Clear what type is expected
   ```

---

## Related Documentation

- **CODESTYLE.md**: Naming conventions for metadata classes
- **TECHNICAL_INSIGHTS_LEGACY_PEAK.md**: Domain-specific parameter values
- **README.txt**: Overall architecture overview

---

**Last Updated:** 2025-11-18
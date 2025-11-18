# Registry System Consolidation Plan

**Issue:** Two different registry implementations with inconsistent APIs
**Created:** 2025-11-18
**Status:** Analysis complete, implementation optional

---

## Problem Statement

The codebase currently has **two different registry patterns** for managing class lookups:

### Registry 1: `ClassRegistry[T]` (Generic, Bidirectional)
**File:** `saxs/saxs/core/kernel/core/registry.py`

**Features:**
- ✅ Generic with TypeVar support
- ✅ Bidirectional mapping (name ↔ class)
- ✅ Type-safe
- ✅ YAML deserialization support
- ✅ Error handling (raises on duplicate registration)

**API:**
```python
registry = ClassRegistry[MyType]()
registry.register("name", MyClass)
cls = registry.get_class("name")        # name → class
name = registry.get_name(MyClass)       # class → name
cls = registry.from_yaml("name")        # Raises if not found
```

**Used For:**
- `StageRegistry = ClassRegistry[IAbstractStage]`
- `PolicyRegistry = ClassRegistry[IAbstractChainingPolicy]`  (alias only!)

---

### Registry 2: `PolicyRegistry` (Specialized, Instance-based)
**File:** `saxs/saxs/core/stage/policy/policy_registry.py`

**Features:**
- ❌ Not generic
- ❌ Unidirectional mapping (stage_cls → policy **instance**)
- ❌ Not type-safe (uses strings in dict)
- ❌ No YAML support
- ✅ Error handling (raises if not found)

**API:**
```python
registry = PolicyRegistry()
registry.register(StageClass, policy_instance)  # Note: instance, not class!
policy = registry.get_policy(StageClass)
```

**Used For:**
- Mapping `IAbstractRequestingStage` → `IAbstractChainingPolicy` **instance**

---

## Key Differences

| Feature | ClassRegistry[T] | PolicyRegistry |
|---------|------------------|----------------|
| **Generics** | ✅ Yes (`TypeVar`) | ❌ No |
| **Bidirectional** | ✅ name ↔ class | ❌ One-way only |
| **Stores** | Classes | **Instances** |
| **Type hints** | Strong | Weak (strings) |
| **YAML support** | ✅ Yes | ❌ No |
| **API consistency** | `register()`, `get_class()`, `get_name()` | `register()`, `get_policy()` |

**Critical Difference:** PolicyRegistry stores **instances**, not classes!

---

## Why Two Different Systems?

### Historical Analysis

Looking at the code, it appears:

1. **ClassRegistry was designed first**
   - Generic, well-thought-out design
   - Intended for all registry needs
   - Type aliases created: `StageRegistry`, `PolicyRegistry`

2. **PolicyRegistry was added later**
   - Solves a specific problem: associating policy **instances** with stage classes
   - Different use case: runtime instance management vs. class lookup

### Use Case Comparison

**ClassRegistry[T]**: "Given a string name, give me the class"
```python
# Use case: Deserialize from YAML
stage_class = stage_registry.from_yaml("CutStage")
stage = stage_class(metadata)
```

**PolicyRegistry**: "Given a stage class, give me its policy instance"
```python
# Use case: Attach policy to dynamically created stage
policy = policy_registry.get_policy(FindPeakStage)
stage = FindPeakStage(policy=policy, metadata=meta)
```

**These are fundamentally different use cases!**

---

## Problem: Name Collision

The confusing part is this line in `registry.py`:

```python
PolicyRegistry = ClassRegistry[IAbstractChainingPolicy]
```

This creates **TWO things called `PolicyRegistry`**:

1. The type alias in `core/kernel/core/registry.py` (maps string → policy **class**)
2. The specialized class in `core/stage/policy/policy_registry.py` (maps stage class → policy **instance**)

**This is the root cause of confusion!**

---

## Solution Options

### Option 1: Rename to Eliminate Confusion ⭐ **RECOMMENDED**

Rename `PolicyRegistry` class to `StagePolicyMapping` to clarify purpose.

**Changes:**
```python
# Before (confusing)
from saxs.saxs.core.stage.policy.policy_registry import PolicyRegistry

# After (clear)
from saxs.saxs.core.stage.policy.stage_policy_mapping import StagePolicyMapping
```

**Files to update:**
- Rename: `policy_registry.py` → `stage_policy_mapping.py`
- Update class name: `PolicyRegistry` → `StagePolicyMapping`
- Update all imports (likely 5-10 files)

**Impact:** Low - Just renaming, no logic changes

**Benefit:** Eliminates name collision and clarifies purpose

---

### Option 2: Consolidate into ClassRegistry (Not Recommended)

Try to make PolicyRegistry use ClassRegistry under the hood.

**Problem:** Different purposes!
- ClassRegistry stores **classes** for deserialization
- PolicyRegistry stores **instances** for runtime association

**Could do:**
```python
class StagePolicyMapping:
    def __init__(self):
        self._registry = ClassRegistry[IAbstractChainingPolicy]()
        self._instances = {}

    def register(self, stage_cls, policy_instance):
        # Store instance separately
        self._instances[stage_cls] = policy_instance
```

**Not worth it** - adds complexity without benefit.

---

### Option 3: Keep Both, Document Clearly ✅ **ACCEPTABLE**

Keep both systems but add clear documentation.

**Changes:**
1. Add docstring to `ClassRegistry` explaining it's for class lookup
2. Add docstring to `PolicyRegistry` explaining it's for instance mapping
3. Update module docstrings
4. **Still rename to avoid collision** (`PolicyRegistry` → `StagePolicyMapping`)

**This document serves as that documentation!**

---

## Metadata Proliferation (6+ Types)

Now let's address the metadata issue.

### Current State

We have 6+ metadata types:

1. **SampleMetadata** - Domain data (experiment info)
2. **FlowMetadata** - Inter-stage communication
3. **StageMetadata** (multiple) - Configuration per stage
4. **EvalMetadata** - Condition evaluation
5. **ApprovalMetadata** - Scheduler decisions
6. **SchedulerMetadata** - Runtime constants

### Is This Really a Problem?

**Arguments FOR keeping 6 types:**
- ✅ Clear separation of concerns
- ✅ Type safety (can't mix up types)
- ✅ Easy to test (mock each independently)
- ✅ Self-documenting code
- ✅ Each has distinct lifecycle

**Arguments AGAINST (complexity):**
- ❌ Cognitive overhead to understand all 6
- ❌ Need to know which type to use when
- ❌ Some overlap (EvalMetadata vs FlowMetadata)

---

## Metadata Simplification Options

### Option A: Merge EvalMetadata into FlowMetadata

**Change:**
```python
# Before
def create_request(metadata: FlowMetadata) -> IAbstractStageRequest:
    eval_metadata = EvalMetadata({...})
    return StageRequest(
        condition_eval_metadata=eval_metadata,
        flow_metadata=metadata
    )

# After
def create_request(metadata: FlowMetadata) -> IAbstractStageRequest:
    return StageRequest(
        condition_eval_metadata=metadata,  # Just use FlowMetadata
        flow_metadata=metadata
    )
```

**Impact:**
- Reduces from 6 to 5 types
- Lose semantic distinction "this data is for eval"
- Minimal code changes (~10 files)

**Recommendation:** ⚠️ **Not worth it** - semantic distinction is valuable

---

### Option B: Create Unified MetadataStore

Single registry holding all metadata with typed accessors.

**Design:**
```python
class MetadataStore:
    def __init__(self):
        self._sample: SampleMetadata = {}
        self._flow: FlowMetadata = {}
        self._config: dict[str, StageMetadata] = {}

    def get_sample(self) -> SampleMetadata:
        return self._sample

    def get_flow(self) -> FlowMetadata:
        return self._flow

    def get_stage_config(self, stage_name: str) -> StageMetadata:
        return self._config[stage_name]
```

**Impact:**
- Major refactoring required
- Changes every stage
- Centralizes all metadata

**Recommendation:** ❌ **Not recommended** - too much disruption for minimal benefit

---

### Option C: Document and Keep Current Structure ✅ **RECOMMENDED**

The 6 metadata types serve distinct purposes. Rather than consolidating, **document clearly**.

**Already done:** `METADATA_HIERARCHY.md` provides:
- ✅ Clear explanation of each type
- ✅ Lifecycle diagrams
- ✅ Usage examples
- ✅ Design rationale

**Additional improvement:**
Add a quick reference chart at the top of key files.

---

## Implementation Priority

### High Priority (Do Now) ⭐

1. **Rename PolicyRegistry → StagePolicyMapping**
   - Eliminates name collision
   - Low effort, high clarity gain
   - Update 5-10 import statements

**Estimated effort:** 30 minutes

---

### Medium Priority (Next Sprint)

2. **Add Registry Documentation**
   - Docstrings explaining when to use which
   - Code examples in docstrings
   - Update module-level docs

**Estimated effort:** 1 hour

---

### Low Priority (Future)

3. **Consider metadata simplification**
   - Only if cognitive overhead becomes a real problem
   - Survey team first - do people find it confusing?
   - Current structure is actually well-designed

**Estimated effort:** N/A (may not be needed)

---

## Recommended Action Plan

### Phase 1: Immediate (This Sprint)

```bash
# 1. Rename PolicyRegistry to StagePolicyMapping
git mv saxs/saxs/core/stage/policy/policy_registry.py \
       saxs/saxs/core/stage/policy/stage_policy_mapping.py

# 2. Update class name in file
sed -i '' 's/class PolicyRegistry/class StagePolicyMapping/g' \
    saxs/saxs/core/stage/policy/stage_policy_mapping.py

# 3. Update all imports
find saxs -name "*.py" -exec sed -i '' \
    's/from saxs\.saxs\.core\.stage\.policy\.policy_registry import PolicyRegistry/from saxs.saxs.core.stage.policy.stage_policy_mapping import StagePolicyMapping/g' {} \;

# 4. Update all usages
find saxs -name "*.py" -exec sed -i '' \
    's/PolicyRegistry(/StagePolicyMapping(/g' {} \;

# 5. Run tests
python3 test.py
```

### Phase 2: Documentation

Update `registry.py` docstring:

```python
"""
Registry module.

This module provides TWO different registry systems:

1. ClassRegistry[T] - Generic class lookup registry
   Use for: String name → Class lookup (deserialization)
   Example: stage_registry.from_yaml("CutStage") → CutStage class

2. StagePolicyMapping - Stage-to-policy instance mapping
   Use for: Stage class → Policy instance (runtime association)
   Example: mapping.get_policy(FindPeakStage) → policy instance
   File: saxs/saxs/core/stage/policy/stage_policy_mapping.py

These serve DIFFERENT purposes and should not be confused!
"""
```

---

## Decision Matrix

| Approach | Effort | Benefit | Risk | Recommended? |
|----------|--------|---------|------|--------------|
| Rename PolicyRegistry | Low (30min) | High (clarity) | Low | ✅ **YES** |
| Document registries | Low (1hr) | Medium | None | ✅ **YES** |
| Consolidate registries | High (days) | Low | High | ❌ **NO** |
| Merge EvalMetadata | Medium (hours) | Low | Medium | ❌ **NO** |
| Metadata unification | Very High (weeks) | Low | Very High | ❌ **NO** |
| Document metadata | Done | High | None | ✅ **DONE** |

---

## Conclusion

### Registry Systems

**Problem:** Name collision between two different registry types
**Solution:** Rename `PolicyRegistry` → `StagePolicyMapping`
**Effort:** 30 minutes
**Status:** Ready to implement

### Metadata Proliferation

**Problem:** 6 types seems like a lot
**Analysis:** Each serves a distinct purpose
**Solution:** Document well (already done)
**Status:** ✅ No action needed - current design is good

---

## Code Examples

### Before (Confusing)

```python
# Which PolicyRegistry is this?!
from saxs.saxs.core.kernel.core.registry import PolicyRegistry  # Type alias
from saxs.saxs.core.stage.policy.policy_registry import PolicyRegistry  # Class

# Conflict!
```

### After (Clear)

```python
# Clear distinction
from saxs.saxs.core.kernel.core.registry import PolicyRegistry  # String → Policy class
from saxs.saxs.core.stage.policy.stage_policy_mapping import StagePolicyMapping  # Stage → Policy instance

# Use case 1: Deserialize policy from YAML
policy_class = PolicyRegistry().from_yaml("SingleStageChainingPolicy")

# Use case 2: Get policy instance for stage
policy_mapping = StagePolicyMapping()
policy_instance = policy_mapping.get_policy(FindPeakStage)
```

---

**Next Steps:**

1. Review this plan
2. Approve rename: `PolicyRegistry` → `StagePolicyMapping`
3. Execute Phase 1 (30 minutes)
4. Update documentation (Phase 2)
5. Close issue

**Last Updated:** 2025-11-18
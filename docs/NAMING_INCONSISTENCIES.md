# Naming Inconsistencies to Fix

**Generated:** 2025-11-18
**Reference:** See CODESTYLE.md for official naming conventions

This document lists all naming inconsistencies in the codebase that should be fixed to comply with the official code style guide.

---

## 1. Abstract Class Naming

**Rule:** Abstract classes should use `IAbstract*` prefix consistently.

### Files to Rename/Refactor:

#### 1.1 `abstr_chaining_policy.py` → `abstract_chaining_policy.py`

**File:** `/saxs/saxs/core/stage/policy/abstr_chaining_policy.py`

**Changes:**
```python
# Current (inconsistent abbreviation)
class AbstractChainingPolicy(ABC):

# Should be:
class IAbstractChainingPolicy(ABC):
```

**Impact:**
- Update all imports of `AbstractChainingPolicy`
- Update subclasses: `SingleStageChainingPolicy`
- Low risk: Only used in policy module

---

#### 1.2 Abstract Scheduler Classes

**File:** `/saxs/saxs/core/pipeline/scheduler/scheduler.py`

**Check for:** Any `AbstractScheduler` classes

**Expected pattern:**
```python
class IAbstractScheduler(ABC):
    """Abstract base for schedulers."""
```

---

#### 1.3 Abstract Kernel Classes

**File:** `/saxs/saxs/core/kernel/core/abstract_kernel.py`

**Check for:** `AbstractKernel` → `IAbstractKernel`

**Expected pattern:**
```python
class IAbstractKernel(ABC):
    """Abstract base for kernels."""
```

---

#### 1.4 Abstract Request Classes

**File:** `/saxs/saxs/core/stage/request/abst_request.py`

**Check for:** `AbstractStageRequest` classes

**Expected:**
```python
class IAbstractStageRequest(ABC):
    """Abstract base for stage requests."""
```

---

#### 1.5 Abstract Stage Request (Scheduler)

**File:** `/saxs/saxs/core/pipeline/scheduler/abstract_stage_request.py`

**Check for:** Classes using `Abstract*` prefix

**Expected:**
```python
class IAbstractStageApprovalRequest(ABC):
    """Abstract base for approval requests."""
```

---

## 2. File Naming Inconsistencies

**Rule:** Prefer full words over abbreviations.

### Files to Rename:

#### 2.1 `abstr_chaining_policy.py` → `abstract_chaining_policy.py`

**Location:** `/saxs/saxs/core/stage/policy/`

**Reason:** Inconsistent abbreviation (`abstr` vs `abstract`)

**Action:**
```bash
git mv abstr_chaining_policy.py abstract_chaining_policy.py
```

**Update imports in:**
- `single_stage_policy.py`
- `__init__.py` (if exists)
- Any other policy files

---

#### 2.2 `abst_request.py` - KEEP AS IS

**Location:** `/saxs/saxs/core/stage/request/`

**Reason:** Grandfather clause - widely used, low value to rename

**Decision:** Keep existing name, but new files should use full `abstract_`

---

## 3. Import Statement Inconsistencies

### Check and Update:

#### 3.1 Logging Imports

**Current patterns found:**
```python
# Pattern 1 (preferred)
from saxs.logging.logger import get_stage_logger
logger = get_stage_logger(__name__)

# Pattern 2 (legacy)
from saxs.logging.logger import get_logger
logger = get_logger(__name__, "stage")
```

**Action:** Standardize to Pattern 1 where possible.

---

#### 3.2 TYPE_CHECKING Imports

**Rule:** Always use `TYPE_CHECKING` block for circular import prevention.

**Files to check:**
- All files importing from `scheduler` in `stage` modules
- All files importing from `pipeline` in `kernel` modules

**Expected pattern:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from saxs.saxs.core.pipeline.scheduler import Scheduler
```

---

## 4. Logging Statement Inconsistencies

**Rule:** Use placeholder format (`%s`), not f-strings.

### Files with f-string logging:

Run this command to find all occurrences:
```bash
rg 'logger\.\w+\(f["\']' saxs/saxs/core saxs/saxs/processing
```

**Fix pattern:**
```python
# ❌ INCORRECT
logger.info(f"Processing {sample_id} with {count} peaks")

# ✅ CORRECT
logger.info("Processing %s with %s peaks", sample_id, count)
```

---

## 5. Module-Level TODO Items

### 5.1 Remove Legacy Directories

**Action:** Archive or delete these directories:
```
/saxs/saxs/saxs/peak/     # Legacy peak detection
/saxs/saxs/saxs/phase/    # Legacy phase classification
/saxs/saxs/saxs/model/    # Empty directory
```

**Before deletion:**
1. ✅ Verify functionality migrated to `/saxs/saxs/processing/`
2. ✅ Extract technical insights (DONE - see TECHNICAL_INSIGHTS_LEGACY_PEAK.md)
3. Archive to separate branch if needed

---

### 5.2 Flatten Directory Structure

**Current:** `/saxs/saxs/saxs/`

**Proposed:**
```
/saxs/
├── core/          # Framework abstractions
├── processing/    # Concrete implementations
├── logging/       # Logging system
└── application/   # Application layer (to be removed)
```

**Impact:** HIGH - requires updating all imports project-wide

**Recommendation:** Plan for major version bump (2.0)

---

## 6. Constant Naming Verification

**Rule:** Module constants should be SCREAMING_SNAKE_CASE.

### Check these files:
- `/saxs/saxs/core/types/scheduler_metadata.py`
- `/saxs/saxs/processing/stage/background/types.py`
- `/saxs/saxs/processing/stage/cut/types.py`

**Verify:**
- All `DEFAULT_*` constants use SCREAMING_SNAKE_CASE
- No lowercase module constants

---

## 7. Class Name Suffix Verification

### 7.1 Verify All Conditions Have `Condition` Suffix

```bash
find saxs/saxs/core/pipeline/condition -name "*.py" -exec grep "^class " {} +
```

**Expected:** All classes should end with `Condition`

---

### 7.2 Verify All Policies Have `Policy` Suffix

```bash
find saxs/saxs/core -name "*policy*.py" -exec grep "^class " {} +
```

**Expected:** All policy classes should end with `Policy`

---

### 7.3 Verify All Stages Have `Stage` Suffix

```bash
find saxs/saxs/processing/stage -name "*.py" -exec grep "^class .*Stage" {} +
```

**Expected:** All stage implementations should end with `Stage`

---

## 8. Metadata Type Naming

**Rule:** Metadata classes should end with `Metadata`, schemas with `MetadataDict`.

### Verify Pattern:

```python
# ✅ CORRECT
class CutStageMetadataDict(TypedDict):
    """Schema definition."""
    cut_point: int

class CutStageMetadata(TAbstractMetadata):
    """Metadata wrapper."""
```

### Files to Check:
- `/saxs/saxs/core/types/stage_metadata.py`
- `/saxs/saxs/core/types/flow_metadata.py`
- All `types.py` files in processing stages

---

## 9. Enum Naming Verification

**Rule:** All enums should have `E*` prefix.

### Check Files:
```bash
find saxs/saxs -name "*.py" -exec grep "class.*Enum" {} +
```

**Verify:**
- `ESAXSSampleKeys`
- `ESampleMetadataKeys`
- `EMetadataSchemaKeys`
- `ERuntimeConstants`
- All other enums

**Fix if found:**
```python
# ❌ INCORRECT
class SampleKeys(Enum):

# ✅ CORRECT
class ESampleKeys(Enum):
```

---

## 10. Priority Action Items

### High Priority (Do First):

1. **Rename `abstr_chaining_policy.py` → `abstract_chaining_policy.py`**
   - Update class name: `AbstractChainingPolicy` → `IAbstractChainingPolicy`
   - Update all imports
   - Run tests

2. **Fix abstract class names:**
   - `AbstractKernel` → `IAbstractKernel`
   - `AbstractScheduler` → `IAbstractScheduler` (if exists)
   - Other `Abstract*` → `IAbstract*`

3. **Standardize logging statements:**
   - Find and replace f-string logging
   - Use component-specific loggers

### Medium Priority (Next Sprint):

4. **Verify and fix enum naming:**
   - Ensure all enums have `E*` prefix

5. **Standardize import patterns:**
   - Use TYPE_CHECKING blocks consistently
   - Use component-specific logger imports

6. **Clean up legacy code:**
   - Archive `/saxs/saxs/saxs/peak/`
   - Archive `/saxs/saxs/saxs/phase/`
   - Remove `/saxs/saxs/saxs/model/`

### Low Priority (Future):

7. **Flatten directory structure** (`/saxs/saxs/saxs/` → `/saxs/`)
   - Requires major refactoring
   - Plan for version 2.0

---

## 11. Automated Checks

### Pre-commit Hook Script

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for f-string logging
if git diff --cached --name-only | grep '\.py$' | xargs grep -n 'logger\.\w\+\(f["\x27]' 2>/dev/null; then
    echo "ERROR: Found f-string in logging statement"
    echo "Use: logger.info('message %s', var) instead of logger.info(f'message {var}')"
    exit 1
fi

# Check for Abstract classes without IAbstract prefix
if git diff --cached --name-only | grep '\.py$' | xargs grep -n '^class Abstract[A-Z].*ABC' 2>/dev/null; then
    echo "ERROR: Found Abstract class without IAbstract prefix"
    echo "Use: class IAbstractName(ABC) instead of class AbstractName(ABC)"
    exit 1
fi

exit 0
```

---

## 12. Verification Commands

### After fixing, run these to verify:

```bash
# 1. Check for f-string logging
rg 'logger\.\w+\(f["\x27]' saxs/saxs/core saxs/saxs/processing

# 2. Check for Abstract* classes (should use IAbstract*)
rg '^class Abstract[A-Z].*\(ABC\)' saxs/saxs/core

# 3. Check for enums without E prefix
rg '^class [A-Z][a-z]+.*\(Enum\)' saxs/saxs

# 4. Check for inconsistent file naming
find saxs/saxs/core -name "*abst*.py" -o -name "*abstr*.py"

# 5. Verify all stages have Stage suffix
find saxs/saxs/processing/stage -name "*.py" -exec grep "^class [A-Z]" {} + | grep -v "Stage\|Dict\|Metadata\|Enum"
```

---

## 13. Migration Checklist

Use this checklist when fixing inconsistencies:

### For Renaming Classes:

- [ ] Update class definition
- [ ] Update all imports
- [ ] Update subclasses/implementations
- [ ] Update type annotations
- [ ] Update docstrings mentioning the class
- [ ] Run tests
- [ ] Update documentation/README

### For Renaming Files:

- [ ] Use `git mv` to preserve history
- [ ] Update all imports
- [ ] Update `__init__.py` if applicable
- [ ] Run tests
- [ ] Update build scripts (if any)
- [ ] Update documentation

### For Fixing Logging:

- [ ] Replace f-strings with placeholders
- [ ] Verify log output unchanged
- [ ] Check performance-critical paths

---

## Document Updates

When fixes are applied:

1. Mark items as complete in this document
2. Update CODESTYLE.md if patterns emerge
3. Add notes on lessons learned

**Last Updated:** 2025-11-18
**Status:** Initial enumeration - no fixes applied yet

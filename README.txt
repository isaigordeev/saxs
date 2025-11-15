
SAXS package
============

SAXS (Small-Angle X-ray Scattering) is a sophisticated framework for
processing and analyzing SAXS data using a modular, pipeline-based
architecture with dynamic stage scheduling, conditional execution,
and extensible processing stages.


Key Features
============

- Modular pipeline architecture with dynamic stage orchestration
- Conditional stage chaining for iterative peak processing
- Policy-based workflow control (insertion & chaining policies)
- Type-safe data structures using TypedDict
- YAML-based pipeline configuration support
- Comprehensive metadata flow between stages
- Extensible stage system with request-approval model
- Processing stages: filtering, background subtraction, peak detection
- Scheduler with pluggable insertion policies
- Comprehensive logging for debugging and monitoring


Architecture Overview
=====================

The SAXS framework implements a layered architecture with the following
key components:

┌────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION LAYER                         │
│  ┌───────────────┐          ┌──────────────────────┐           │
│  │  YAML Config  │   OR     │  Python Kernel Code  │           │
│  └───────┬───────┘          └───────────┬──────────┘           │
└──────────┼──────────────────────────────┼──────────────────────┘
           │                              │
           ▼                              ▼
┌────────────────────────────────────────────────────────────────┐
│                     KERNEL LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     BaseKernel                           │  │
│  │  - Orchestrates pipeline building                        │  │
│  │  - Coordinates compiler & scheduler                      │  │
│  │  - Manages sample creation & execution                   │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└───────────────────────┼────────────────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────────────────┐
│                    COMPILER LAYER                              │
│  ┌─────────────────┐      ┌────────────────┐                   │
│  │ Frontend        │──────│ Backend        │                   │
│  │ - YAML Parser   │      │ - Builder      │                   │
│  │ - Decl Specs    │      │ - Linker       │                   │
│  └─────────────────┘      └────────────────┘                   │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      Pipeline                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │              BaseScheduler (FIFO Queue)            │  │  │
│  │  │  - Pops stages from queue                          │  │  │
│  │  │  - Executes stage.process()                        │  │  │
│  │  │  - Evaluates stage requests via policies           │  │  │
│  │  │  - Enqueues approved stages                        │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                     STAGE LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ IAbstract    │  │ IAbstract    │  │ Composite    │          │
│  │ Stage        │  │ Requesting   │  │ Requesting   │          │
│  │              │  │ Stage        │  │ Stage        │          │
│  │ - _process() │  │ - create_    │  │ (wrapper)    │          │
│  │   method     │  │   request()  │  │              │          │
│  └──────────────┘  │ - request_   │  └──────────────┘          │
│                    │   stage()    │                            │
│                    └──────────────┘                            │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                    POLICY LAYER                                │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │  Chaining Policies   │    │ Insertion Policies   │          │
│  │  - Single Stage      │    │ - Always Insert      │          │
│  │  - Multi Stage       │    │ - Never Insert       │          │
│  │  - Uses Conditions   │    │ - Saturation         │          │
│  └──────────────────────┘    │ - Metadata Key       │          │
│                              └──────────────────────┘          │
└───────────────────────────────┬────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                   CONDITION LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  StageCondition (evaluates EvalMetadata)                 │  │
│  │  - ChainingPeakCondition: checks unprocessed peaks       │  │
│  │  - ThresholdCondition: numeric thresholds                │  │
│  │  - MetadataCondition: metadata key checks                │  │
│  │  - TrueCondition: always true                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘


Data Flow
=========

┌──────────────┐
│ DataReader   │  Reads CSV (q, intensity, error)
│ (CSV input)  │
└──────┬───────┘
       │
       ▼
┌───────────────────────────────────────────────────────────────┐
│                        SAXSSample                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  q_values    │  │  intensity   │  │  intensity_  │         │
│  │  (array)     │  │  (array)     │  │  error       │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  metadata (SampleMetadata)                               │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Kernel.run(sample)    │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Pipeline.run(sample)  │
                    └────────────┬───────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────┐
              │  Scheduler executes stages:      │
              └──────────────────────────────────┘
                                 │
       ┌─────────────────────────┼─────────────────────────┐
       │                         │                         │
       ▼                         ▼                         ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  CutStage    │   →    │ FilterStage  │   →    │ Background   │
│              │        │              │        │ Stage        │
└──────────────┘        └──────────────┘        └──────┬───────┘
                                                       │
                                                       ▼
                                              ┌──────────────┐
                                              │ FindPeak     │
                                              │ Stage        │
                                              └──────┬───────┘
                                                     │
                  ┌──────────────────────────────────┘
                  │ Request ProcessPeakStage for each peak
                  │ (if ChainingPeakCondition = true)
                  ▼
         ┌──────────────────┐
         │ ProcessPeak      │
         │ Stage            │◄─────────┐
         └──────┬───────────┘          │
                │                      │
                │ Request FindPeak     │
                │ again (loop)         │
                └──────────────────────┘
                         │
                         │ (Until no unprocessed peaks)
                         ▼
                ┌──────────────────┐
                │ Processed Sample │
                └──────────────────┘


Stage Execution Flow
=====================

For each stage in the scheduler queue:

1. stage.process(sample, flow_metadata)
   │
   ├─► _prehandle_flow_metadata(sample, flow_metadata)
   │   └─► Update sample from flow metadata
   │
   ├─► _process(sample, flow_metadata)
   │   └─► Transform data (core logic)
   │
   └─► _posthandle_flow_metadata(sample, flow_metadata)
       └─► Update flow metadata from sample

2. stage.request_stage(flow_metadata)
   │
   ├─► create_request(flow_metadata)
   │   └─► Build StageRequest with EvalMetadata
   │
   └─► chaining_policy.build_approval_requests(request)
       │
       ├─► condition.evaluate(eval_metadata)
       │   └─► True/False
       │
       └─► Return list of StageApprovalRequest

3. For each approval request:
   │
   └─► insertion_policy.approve(request, metadata)
       │
       ├─► True  → scheduler.enqueue(stage)
       └─► False → discard request


Directory Structure
===================

saxs/
├── saxs/
│   ├── __init__.py              # Package constants
│   ├── application/             # Legacy application layer
│   ├── logging/                 # Logging utilities
│   └── saxs/                    # Core SAXS package
│       ├── core/                # Core architecture (~3600 LOC)
│       │   ├── data/
│       │   │   └── reader.py            # DataReader
│       │   ├── kernel/
│       │   │   ├── core/
│       │   │   │   ├── abstract_kernel.py
│       │   │   │   ├── base_kernel.py   # BaseKernel
│       │   │   │   ├── back/            # Compiler backend
│       │   │   │   │   ├── kernel_compiler.py
│       │   │   │   │   ├── pipeline_spec_compiler.py
│       │   │   │   │   ├── stage_builder.py
│       │   │   │   │   ├── policy_builder.py
│       │   │   │   │   ├── stage_linker.py
│       │   │   │   │   ├── policy_linker.py
│       │   │   │   │   └── buffer.py
│       │   │   │   └── front/           # YAML frontend
│       │   │   │       ├── parser.py
│       │   │   │       └── declarative_specs.py
│       │   │   └── registry/
│       │   │       └── kernel_registry.py
│       │   ├── pipeline/
│       │   │   ├── pipeline.py          # Pipeline class
│       │   │   ├── scheduler/
│       │   │   │   ├── scheduler.py     # BaseScheduler
│       │   │   │   ├── abstract_stage_request.py
│       │   │   │   └── policy/
│       │   │   │       └── insertion_policy.py
│       │   │   └── condition/
│       │   │       ├── abstract_condition.py
│       │   │       ├── chaining_condition.py
│       │   │       ├── threshold_condition.py
│       │   │       ├── metadata_condition.py
│       │   │       └── constant_true_condition.py
│       │   ├── stage/
│       │   │   ├── abstract_stage.py
│       │   │   ├── abstract_cond_stage.py
│       │   │   ├── compose_stage.py
│       │   │   ├── policy/
│       │   │   │   ├── abstr_chaining_policy.py
│       │   │   │   ├── single_stage_policy.py
│       │   │   │   └── policy_registry.py
│       │   │   └── request/
│       │   │       └── abst_request.py
│       │   └── types/
│       │       ├── abstract_data.py
│       │       ├── sample.py             # SAXSSample
│       │       ├── sample_objects.py
│       │       ├── metadata.py
│       │       ├── flow_metadata.py
│       │       ├── stage_metadata.py
│       │       └── scheduler_metadata.py
│       ├── processing/          # Concrete implementations
│       │   ├── functions.py
│       │   ├── kernel/
│       │   │   └── default_kernel.py
│       │   ├── stage/
│       │   │   ├── background/
│       │   │   │   └── background.py     # BackgroundStage
│       │   │   ├── cut/
│       │   │   │   └── cut.py            # CutStage
│       │   │   ├── filter/
│       │   │   │   ├── filter.py         # FilterStage
│       │   │   │   └── smooth_stage.py
│       │   │   ├── peak/
│       │   │   │   ├── find_peak.py      # FindPeakStage
│       │   │   │   └── process_peak.py   # ProcessPeakStage
│       │   │   ├── phase/
│       │   │   └── common/
│       │   │       └── fitting.py
│       │   └── yaml/
│       │       └── kernel.yaml           # YAML pipeline config
│       ├── peak/                # Legacy peak classification
│       ├── phase/               # Legacy phase classification
│       └── model/
├── tests/                       # Comprehensive test suite
├── arch/                        # Architecture visualization
│   └── graph.py
├── pyproject.toml
└── README.txt


Processing Stages
=================

Core Stages (saxs/saxs/processing/stage/):

┌────────────────────────────────────────────────────────────────┐
│ CutStage                                                       │
│ - Truncates data at specified index                            │
│ - Parameters: cut_point (int)                                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ FilterStage                                                    │
│ - Filters/smooths intensity data                               │
│ - Parameters: filter_type, window_length, polyorder            │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ BackgroundStage                                                │
│ - Fits hyperbolic background: I(q) = a/(q-b) + c               │
│ - Subtracts fitted background from intensity                   │
│ - Parameters: fit_range, initial_params                        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ FindPeakStage (IAbstractRequestingStage)                       │
│ - Detects peaks using scipy.signal.find_peaks                  │
│ - Stores unprocessed_peaks in FlowMetadata                     │
│ - Requests ProcessPeakStage for each peak                      │
│ - Uses ChainingPeakCondition                                   │
│ - Parameters: prominence, height, distance                     │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ProcessPeakStage (IAbstractRequestingStage)                    │
│ - Processes single peak from metadata.current_peak             │
│ - Moves peak from unprocessed to processed                     │
│ - Requests FindPeakStage again (loop continuation)             │
│ - Uses TrueCondition                                           │
│ - Parameters: peak processing config                           │
└────────────────────────────────────────────────────────────────┘


Peak Processing Loop
====================

The iterative peak processing demonstrates the power of the
request-approval architecture:

Step 1: FindPeakStage executes
   ├─► Finds all peaks: {peak1, peak2, peak3}
   ├─► Sets flow_metadata.unprocessed_peaks = {peak1, peak2, peak3}
   ├─► Sets flow_metadata.current_peak = peak1
   └─► Requests ProcessPeakStage via SingleStageChainingPolicy
       └─► ChainingPeakCondition.evaluate()
           └─► Returns True (current_peak is defined)

Step 2: Scheduler evaluates request
   └─► InsertionPolicy.approve()
       └─► Returns True (e.g., SaturationInsertPolicy count < 6)
       └─► Enqueues ProcessPeakStage

Step 3: ProcessPeakStage executes
   ├─► Processes peak1
   ├─► Moves peak1: unprocessed → processed
   ├─► Sets current_peak = peak2 (next unprocessed)
   └─► Requests FindPeakStage via SingleStageChainingPolicy
       └─► TrueCondition.evaluate()
           └─► Returns True (always)

Step 4: FindPeakStage executes again
   └─► (Repeats from Step 1 with peak2)

Loop continues until:
   - unprocessed_peaks is empty, OR
   - InsertionPolicy rejects request (e.g., saturation limit)


Metadata System
===============

Three types of metadata flow through the pipeline:

┌────────────────────────────────────────────────────────────────┐
│ FlowMetadata                                                   │
│ - Flows between stages                                         │
│ - Contains: processed_peaks, unprocessed_peaks, current_peak   │
│ - Updated by _prehandle_flow_metadata()                        │
│ - Updated by _posthandle_flow_metadata()                       │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ StageMetadata                                                  │
│ - Stage-specific metadata                                      │
│ - Stored in sample.metadata                                    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ EvalMetadata                                                   │
│ - Lightweight metadata for condition evaluation                │
│ - Extracted from FlowMetadata                                  │
│ - Used by StageCondition.evaluate()                            │
└────────────────────────────────────────────────────────────────┘


Policy System
=============

Chaining Policies (Stage-level):
   Determine which stages to request after current stage

   ┌─────────────────────────────────────────────────────────┐
   │ SingleStageChainingPolicy                               │
   │ - Requests single stage based on condition              │
   │ - evaluate(condition, eval_metadata) → True/False       │
   │ - Returns [StageApprovalRequest] or []                  │
   └─────────────────────────────────────────────────────────┘

Insertion Policies (Scheduler-level):
   Control whether scheduler accepts requested stages

   ┌─────────────────────────────────────────────────────────┐
   │ AlwaysInsertPolicy        │ Accept all requests         │
   ├───────────────────────────┼─────────────────────────────┤
   │ NeverInsertPolicy         │ Reject all requests         │
   ├───────────────────────────┼─────────────────────────────┤
   │ SaturationInsertPolicy    │ Accept up to N requests     │
   ├───────────────────────────┼─────────────────────────────┤
   │ MetadataKeyPolicy         │ Accept if key in metadata   │
   └─────────────────────────────────────────────────────────┘


Getting Started
===============

-------------------------------------------------------------------
Example 1: Basic Pipeline Execution
-------------------------------------------------------------------

from saxs.saxs.core.data.reader import DataReader
from saxs.saxs.processing.kernel.default_kernel import DefaultKernel
from saxs.saxs.core.pipeline.scheduler.scheduler import BaseScheduler
from saxs.saxs.core.pipeline.scheduler.policy.insertion_policy import (
    SaturationInsertPolicy
)

# 1. Read data
data_reader = DataReader("path/to/data.csv")
q, i, di = data_reader.read_data()
sample = data_reader.create_sample(q, i, di)

# 2. Configure scheduler with insertion policy
insertion_policy = SaturationInsertPolicy(max_insertions=6)
scheduler = BaseScheduler(insertion_policy=insertion_policy)

# 3. Create kernel and run pipeline
kernel = DefaultKernel(scheduler=scheduler)
processed_sample = kernel.run(sample)

# 4. Access results
processed_intensity = processed_sample['intensity']
metadata = processed_sample['metadata']

-------------------------------------------------------------------
Example 2: YAML-Based Configuration
-------------------------------------------------------------------

from saxs.saxs.core.kernel.core.base_kernel import BaseKernel
from saxs.saxs.core.kernel.core.back.kernel_compiler import YamlCompiler

# Load YAML pipeline configuration
yaml_path = "saxs/saxs/processing/yaml/kernel.yaml"
compiler = YamlCompiler(yaml_path)

# Create and run kernel
kernel = BaseKernel(compiler=compiler, scheduler=scheduler)
processed_sample = kernel.run(sample)

-------------------------------------------------------------------
Example 3: Custom Stage Implementation
-------------------------------------------------------------------

from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.sample import SAXSSample
from saxs.saxs.core.types.flow_metadata import FlowMetadata

class MyCustomStage(IAbstractStage):
    def __init__(self, param1, param2):
        super().__init__(stage_name="MyCustomStage")
        self.param1 = param1
        self.param2 = param2

    def _process(
        self,
        sample: SAXSSample,
        flow_metadata: FlowMetadata
    ) -> tuple[SAXSSample, FlowMetadata]:
        # Transform data
        new_intensity = sample['intensity'] * self.param1

        # Update sample
        updated_sample = sample.copy()
        updated_sample['intensity'] = new_intensity

        return updated_sample, flow_metadata

-------------------------------------------------------------------
Example 4: Custom Condition
-------------------------------------------------------------------

from saxs.saxs.core.pipeline.condition.abstract_condition import (
    StageCondition
)
from saxs.saxs.core.stage.request.abst_request import EvalMetadata

class MyCustomCondition(StageCondition):
    def __init__(self, threshold: float):
        self.threshold = threshold

    def evaluate(self, eval_metadata: EvalMetadata) -> bool:
        # Custom evaluation logic
        return eval_metadata.get('some_value', 0) > self.threshold


Contribute
==========

-------------------------------------------------------------------
1. Install the dependencies as defined in `pyproject.toml`.
-------------------------------------------------------------------

    > uv venv

-------------------------------------------------------------------
2. Testing
-------------------------------------------------------------------

Tests can be found in the `tests/` directory.


License
=======

This project is under the MIT license
            (specified in the LICENSE file)

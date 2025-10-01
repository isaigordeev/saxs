# SAXS analyse

Gaussian processing and transformer model for classification SAXS data

for running

choose peak and phase kernels (algorithms of classification) for your data
and its paths to .csv files.

after call an instance of manager class.

# todo

- Replace deque.popleft() → use list + index to avoid function call overhead.
- Batch process samples → if stages can handle arrays, vectorize NumPy operations.
- Minimize Python object creation → reuse metadata, requests, and temporary objects.
- Use numba / JIT compilation → compile loops if Python overhead dominates.
- Parallelize independent stages → with ThreadPoolExecutor if process releases GIL.
- better scheduler metadata
- better type hierachy (with more abstaction and more usefullness)

# ?

- inplace ops?
- instance or class injections?
- lambda for state factory in injections?
- metaclass for logging
- pydantic for gluing metadata between stages
- replace python func calc in processing by cpp ones
  – pipeline scheduler for peaks in order (map reduce like) for multiprocessing
- composite stage
- new frontend yaml
  - parser verifier
- new backend with decl specs

## ??

```
from saxs.application.manager import Manager

from saxs.saxs.peak.parabole_kernel import (
    RobustParabolePeakKernel,
)
from saxs.saxs.phase.default_kernel import DefaultPhaseKernel

# a = ProminenceKernel('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data/075775_treated_xye.csv')

# a = PeakApplication('/Users/isaigordeev/Desktop/2023/saxs/test_processing_data', ParabolePeakKernel)
# a.peak_classification()

# b = PhaseApplication('/Users/isaigordeev/Desktop/2023/saxs/results/session_results/2023-07-28/22:57:00_prominence_kernel.json', AbstractPhaseKernel)
# b.phase_classification()

# a = Manager(peak_kernel=ParabolePeakKernel, phase_kernel=DefaultPhaseKernel)
a = Manager(
    peak_data_path="tests/test_processing_data",
    peak_kernel=RobustParabolePeakKernel,
    phase_kernel=DefaultPhaseKernel,
)
# a = Manager(peak_data_directory='res/', peak_kernel=RobustParabolePeakKernel, phase_kernel=DefaultPhaseKernel)

# a = Manager(peak_kernel=ProminencePeakKernel, phase_kernel=DefaultPhaseKernel)
a()

# if __main__ == '__main__'
# a()
# test.directory_processing()
```

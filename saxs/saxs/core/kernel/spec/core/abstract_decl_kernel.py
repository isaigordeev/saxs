from typing import List

from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.kernel.forward.core.abstract_kernel import (
    AbstractKernel,
)
from saxs.saxs.core.kernel.spec.back.runtime_spec import PolicySpec, StageSpec


class AbstractKernelSpec(AbstractKernel):
    def define_pipeline(self) -> List[StageSpec]:
        raise NotImplementedError()

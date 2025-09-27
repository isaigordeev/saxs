from typing import List
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.processing.kernel.nested_kernel.core.abstract_kernel import (
    AbstractKernel,
)
from saxs.saxs.processing.kernel.stage_spec import StageSpec


class SimpleKernelSpec(AbstractKernel):
    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    def define_pipeline(self) -> List[StageSpec]: ...

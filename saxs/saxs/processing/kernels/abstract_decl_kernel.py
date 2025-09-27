from typing import List
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.processing.kernels.abstract_kernel import AbstractKernel
from saxs.saxs.processing.kernels.stage_spec import StageSpec


class SimpleKernelSpec(AbstractKernel):
    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    def define_pipeline(self) -> List[StageSpec]: ...

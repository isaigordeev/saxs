from typing import List

from saxs.saxs.core.kernel.nested.core.abstract_kernel import (
    AbstractKernel,
)
from saxs.saxs.core.kernel.decl.stage_spec import StageSpec

from saxs.saxs.core.data.sample import SAXSSample


class AbstractKernelSpec(AbstractKernel):
    def create_sample(self, data: dict) -> "SAXSSample":
        return SAXSSample(data=data)

    def define_pipeline(self) -> List[StageSpec]: ...

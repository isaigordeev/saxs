from typing import Dict, List

from saxs.saxs.core.kernel.spec.back.runtime_spec import StageSpec
from saxs.saxs.core.kernel.spec.back.stage_builder import StageBuilder
from saxs.saxs.core.kernel.spec.back.stage_linker import StageLinker
from saxs.saxs.core.stage.abstract_cond_stage import AbstractStage


class StagePipelineBuilder:
    """
    Orchestrates building and linking of stages from StageSpec list.
    Maintains SOLID separation:
      - StageBuilder: creates stage instances
      - StageLinker: attaches policies and resolves next stages.
    """

    def __init__(self, stage_specs: List[StageSpec]):
        self.stage_specs = stage_specs
        self.stage_instances: Dict[str, AbstractStage] = {}

    def build(self) -> List[AbstractStage]:
        """
        Build and link stages. Returns ordered list of stage instances.
        """
        # Step 1: Build stage instances
        self.stage_instances = StageBuilder.build(self.stage_specs)

        # Step 2: Link policies and next-stage references
        StageLinker.link(self.stage_specs, self.stage_instances)

        # Step 3: Return ordered list
        return [self.stage_instances[spec.id] for spec in self.stage_specs]

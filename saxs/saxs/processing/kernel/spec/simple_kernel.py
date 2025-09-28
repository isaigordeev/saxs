from typing import List
from saxs.saxs.core.data.sample import SAXSSample
from saxs.saxs.core.kernel.spec.back.runtime_spec import StageSpec, PolicySpec
from saxs.saxs.core.kernel.spec.back.buffer import (
    StageRegistryBuffer,
    PolicyRegistryBuffer,
)
from saxs.saxs.core.kernel.spec.back.pipeline_builder import (
    StagePipelineBuilder,
)
from saxs.saxs.core.pipeline.condition.chaining_condition import (
    ChainingPeakCondition,
)
from saxs.saxs.core.stage.policy.single_stage_policy import (
    SingleStageChainingPolicy,
)
from saxs.saxs.core.kernel.forward.core.base_kernel import BaseKernel
from saxs.saxs.processing.stage.filter.background_stage import BackgroundStage
from saxs.saxs.processing.stage.filter.cut_stage import CutStage
from saxs.saxs.processing.stage.filter.filter_stage import FilterStage
from saxs.saxs.processing.stage.peak.find_peak_stage import FindAllPeaksStage
from saxs.saxs.processing.stage.peak.process_peak_stage import (
    ProcessFitPeakStage,
)


class SimpleKernel(BaseKernel):
    def create_sample(self, data: dict) -> SAXSSample:
        return SAXSSample(data=data)

    def define_pipeline(self) -> List[StageSpec]:
        """
        Define pipeline declaratively using StageSpec and PolicySpec.
        Policies reference stages by ID (no class instances here yet).
        """
        # Define policies first
        peaks_policy = PolicySpec(
            id="peaks_policy",
            policy_cls=SingleStageChainingPolicy,
            condition_cls=ChainingPeakCondition,
            condition_kwargs={"key": "peaks"},
            next_stage_id=["process_fit_peak"],
        )

        # Define stages
        pipeline = [
            StageSpec(
                id="cut",
                stage_cls=CutStage,
                kwargs={"cut_point": 200},
            ),
            StageSpec(
                id="filter",
                stage_cls=FilterStage,
            ),
            StageSpec(
                id="background",
                stage_cls=BackgroundStage,
            ),
            StageSpec(
                id="find_peaks",
                stage_cls=FindAllPeaksStage,
                policy=peaks_policy,
            ),
            StageSpec(
                id="process_fit_peak",
                stage_cls=ProcessFitPeakStage,
            ),
        ]

        return pipeline

    def build_runtime_pipeline(self):
        """
        Example of building actual stage instances from StageSpec/PolicySpec.
        """
        stage_buffer = StageRegistryBuffer()
        policy_buffer = PolicyRegistryBuffer()

        # Register policies
        for stage in self.define_pipeline():
            if stage.policy:
                policy_buffer.register(stage.policy.id, stage.policy)
            stage_buffer.register(stage.id, stage)

        # Build and link stage instances
        builder = StagePipelineBuilder(stage_buffer, policy_buffer)
        runtime_stages = builder.build()
        return runtime_stages

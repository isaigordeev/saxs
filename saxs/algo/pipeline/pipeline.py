#
# Created by Isai GORDEEV on 19/09/2025.
#

from saxs.algo.data.sample import SAXSSample
from saxs.algo.pipeline.stage.abstract_stage import AbstractStage


class Pipeline:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage: AbstractStage):
        self.stages.append(stage)
        return self  # allow chaining

    def run(self, data: SAXSSample) -> SAXSSample:
        for stage in self.stages:
            data = stage.process(data)
        return data

from saxs.algo.data.stage import SAXSSample
from saxs.algo.pipeline.stage.abstract_stage import Stage


class Pipeline:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage: Stage):
        self.stages.append(stage)
        return self  # allow chaining

    def run(self, data: SAXSSample) -> SAXSSample:
        for stage in self.stages:
            data = stage.process(data)
        return data

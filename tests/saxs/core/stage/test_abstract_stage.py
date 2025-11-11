# Created by Isai Gordeev on 20/09/2025.

"""Tests for abstract_stage.py module."""

from unittest.mock import Mock

import numpy as np
import pytest
from saxs.saxs.core.pipeline.condition.abstract_condition import (
    SampleCondition,
)
from saxs.saxs.core.stage.abstract_cond_stage import AbstractConditionalStage
from saxs.saxs.core.stage.abstract_stage import IAbstractStage
from saxs.saxs.core.types.sample_objects import SampleMetadata
from saxs.saxs.core.types.stage_metadata import TAbstractStageMetadata


@pytest.fixture
def saxs_sample():
    """Minimal SAXSSample for testing."""
    from saxs.saxs.core.types.sample import SAXSSample
    from saxs.saxs.core.types.sample_objects import (
        Intensity,
        IntensityError,
        QValues,
    )

    q = QValues(np.array([0.1, 0.2, 0.3]))
    i = Intensity(np.array([1.0, 2.0, 3.0]))
    err = IntensityError(np.array([0.01, 0.02, 0.03]))
    meta = SampleMetadata({"source": "test"})
    return SAXSSample(
        q_values=q,
        intensity=i,
        intensity_error=err,
        metadata=meta,
    )


@pytest.fixture
def mock_stage():
    """Mock stage with process and request_stage."""
    stage = Mock()
    stage.metadata = TAbstractStageMetadata({"name": "mock_stage"})
    stage.process = Mock()
    stage.request_stage.return_value = []
    return stage


class ConcreteConditionalStage(AbstractConditionalStage):
    def _process(self, stage_data):
        new_stage_ = stage_data.set_intensity(
            stage_data.get_intensity_array() * 2,
        )

        return new_stage_, {"max_I": max(new_stage_.get_intensity_array())}


class TestAbstractStage:
    """Tests for AbstractStage."""

    def test_abstract_stage_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            IAbstractStage()

    def test_abstract_stage_has_methods(self) -> None:
        assert hasattr(IAbstractStage, "process")
        assert callable(IAbstractStage.process)
        assert hasattr(IAbstractStage, "_process")
        assert callable(IAbstractStage._process)
        assert hasattr(IAbstractStage, "request_stage")
        assert callable(IAbstractStage.request_stage)

    def test_concrete_stage_process(self, saxs_sample) -> None:
        """Test minimal concrete subclass of AbstractStage."""

        class ConcreteStage(IAbstractStage):
            def __init__(self):
                self.metadata = TAbstractStageMetadata({"name": "concrete"})

            def _process(self, stage_data):
                return stage_data, None

            def request_stage(self):
                return []

        stage = ConcreteStage()
        result = stage.process(saxs_sample)
        assert result == saxs_sample
        assert stage.request_stage() == []

    def test_stage_with_metadata(self, saxs_sample) -> None:
        class MetadataStage(IAbstractStage):
            def __init__(self):
                self.metadata = TAbstractStageMetadata(
                    {"name": "meta", "type": "test"},
                )

            def _process(self, stage_data):
                return stage_data, None

            def request_stage(self):
                return []

        stage = MetadataStage()
        assert stage.metadata.unwrap()["name"] == "meta"
        assert stage.metadata.unwrap()["type"] == "test"
        result = stage.process(saxs_sample)
        assert result == saxs_sample

    def test_chaining_stage(self, saxs_sample) -> None:
        class ChainingStage(IAbstractStage):
            def __init__(self, next_stages=None):
                self.metadata = TAbstractStageMetadata({"name": "chain"})
                self.next_stages = next_stages or []

            def _process(self, stage_data):
                return stage_data

            def request_stage(self):
                return self.next_stages

        stage1 = ChainingStage()
        assert stage1.request_stage() == []

        next_stage1 = Mock()
        next_stage2 = Mock()
        stage2 = ChainingStage([next_stage1, next_stage2])
        assert stage2.request_stage() == [next_stage1, next_stage2]

    def test_processing_stage_modifies_sample(self, saxs_sample) -> None:
        class ProcessingStage(IAbstractStage):
            def __init__(self, multiplier=2.0):
                self.metadata = TAbstractStageMetadata({"name": "proc"})
                self.multiplier = multiplier

            def _process(self, stage_data):
                arr = stage_data.get_intensity_array()
                new_arr = arr * self.multiplier
                return stage_data.set_intensity(new_arr), None

            def request_stage(self):
                return []

        stage = ProcessingStage(multiplier=3.0)
        result = stage.process(saxs_sample)
        np.testing.assert_array_equal(
            result.get_intensity_array(),
            saxs_sample.get_intensity_array() * 3.0,
        )

    def test_error_stage_raises(self, saxs_sample) -> None:
        class ErrorStage(IAbstractStage):
            def __init__(self, should_raise=False):
                self.metadata = TAbstractStageMetadata({"name": "err"})
                self.should_raise = should_raise

            def _process(self, stage_data):
                if self.should_raise:
                    msg = "Processing failed"
                    raise ValueError(msg)
                return stage_data, None

            def request_stage(self):
                return []

        stage_ok = ErrorStage(False)
        result = stage_ok.process(saxs_sample)
        assert result == saxs_sample

        stage_fail = ErrorStage(True)
        with pytest.raises(ValueError, match="Processing failed"):
            stage_fail.process(saxs_sample)


class TestAbstractConditionalStage:
    """Tests for AbstractConditionalStage."""

    def test_creation_with_concrete_subclass(
        self,
        mock_stage,
        saxs_sample,
    ) -> None:
        from saxs.saxs.core.pipeline.condition.abstract_condition import (
            SampleCondition,
        )

        class ConcreteConditionalStage(AbstractConditionalStage):
            def _process(self, stage_data):
                return stage_data, None

        condition = Mock(spec=SampleCondition)
        stage = ConcreteConditionalStage(
            chaining_stage=mock_stage,
            condition=condition,
        )

        assert stage.chaining_stage is not None
        assert stage.condition is not None


class MaxIntensityCondition(SampleCondition):
    """Concrete SampleCondition that passes if sample's max intensity exceeds
    threshold.
    """

    def __init__(self, threshold: float):
        self.threshold = threshold

    def evaluate(self, metadata):
        return metadata.unwrap().get("max_I") > self.threshold


class TestAbstractConditionalStageAdvanced:
    """Tests for AbstractConditionalStage with real condition logic."""

    def test_conditional_stage_runs_only_if_condition_true(
        self,
        saxs_sample,
    ) -> None:
        # Threshold lower than max intensity → condition True
        condition = MaxIntensityCondition(threshold=1.5)
        stage = ConcreteConditionalStage(
            chaining_stage=ConcreteConditionalStage,
            condition=condition,
        )

        result = stage.process(saxs_sample)
        # Because condition is True, _process should run and intensities doubled
        np.testing.assert_array_equal(
            result.get_intensity_array(),
            saxs_sample.get_intensity_array() * 2,
        )

        requests = stage.request_stage()

        assert len(requests) == 1

    def test_conditional_stage_skips_if_condition_false(
        self,
        saxs_sample,
    ) -> None:
        # Threshold higher than max intensity → condition False
        condition = MaxIntensityCondition(threshold=10.0)
        stage = ConcreteConditionalStage(
            chaining_stage=None,
            condition=condition,
        )

        result = stage.process(saxs_sample)
        # Because condition is False, _process should not modify sample
        np.testing.assert_array_equal(
            result.get_intensity_array(),
            saxs_sample.get_intensity_array() * 2,
        )

        requests = stage.request_stage()

        assert requests == []

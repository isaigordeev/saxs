"""Test script to demonstrate the enhanced logging system.

This script showcases the new colorful, modular logging system
with component-specific formatters and visual hierarchy.
"""

import logging

from saxs.logging.logger import (
    get_kernel_logger,
    get_logger,
    get_pipeline_logger,
    get_scheduler_logger,
    get_stage_logger,
    setup_logging,
)


def test_basic_logging() -> None:
    """Test basic logging functionality."""
    logger = get_logger(__name__, "default")

    logger.header("BASIC LOGGING TEST")
    logger.info("This is an info message")
    logger.debug("This is a debug message (won't show at INFO level)")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.separator()


def test_component_loggers() -> None:
    """Test component-specific loggers."""
    scheduler_logger = get_scheduler_logger("test.scheduler")
    stage_logger = get_stage_logger("test.stage")
    kernel_logger = get_kernel_logger("test.kernel")
    pipeline_logger = get_pipeline_logger("test.pipeline")

    # Scheduler logging
    scheduler_logger.header("SCHEDULER COMPONENT TEST")
    scheduler_logger.scheduler_info(
        "Initializing scheduler",
        queue_size=5,
        policy="SaturationInsertPolicy",
    )
    scheduler_logger.scheduler_info(
        "Processing stage",
        queue_size=4,
        stage="CutStage",
    )
    scheduler_logger.success("Stage completed successfully")
    scheduler_logger.separator()

    # Stage logging
    stage_logger.header("STAGE COMPONENT TEST")
    stage_logger.stage_info(
        "FindPeakStage",
        "Detecting peaks",
        data_points=1000,
        peaks_found=5,
    )
    stage_logger.stage_info(
        "ProcessPeakStage",
        "Processing peak",
        peak_index=42,
        prominence=0.85,
    )
    stage_logger.success("Peak processing completed")
    stage_logger.separator()

    # Kernel logging
    kernel_logger.header("KERNEL COMPONENT TEST")
    kernel_logger.kernel_info(
        "Building pipeline",
        stages_count=4,
        compiler="YamlCompiler",
    )
    kernel_logger.kernel_info(
        "Compiling stages",
        compiled=True,
    )
    kernel_logger.success("Kernel initialization complete")
    kernel_logger.separator()

    # Pipeline logging
    pipeline_logger.header("PIPELINE COMPONENT TEST")
    pipeline_logger.pipeline_info(
        "Starting pipeline execution",
        stages=["CutStage", "FilterStage", "BackgroundStage"],
    )
    pipeline_logger.pipeline_info(
        "Pipeline progress",
        current_stage="BackgroundStage",
        progress="75%",
    )
    pipeline_logger.success("Pipeline execution finished")
    pipeline_logger.separator()


def test_visual_elements() -> None:
    """Test visual elements like steps, sections, headers."""
    logger = get_scheduler_logger("test.visual")

    logger.header("VISUAL ELEMENTS TEST", "=", 80)

    logger.section("Data Loading")
    logger.step(1, "Loading CSV file")
    logger.step(2, "Parsing intensity data")
    logger.step(3, "Creating SAXSSample")
    logger.success("Data loading complete")

    logger.section("Processing Pipeline")
    logger.step(1, "Executing CutStage")
    logger.progress("Processing CutStage...")
    logger.success("CutStage completed")

    logger.step(2, "Executing FilterStage")
    logger.progress("Processing FilterStage...")
    logger.success("FilterStage completed")

    logger.step(3, "Executing FindPeakStage")
    logger.progress("Processing FindPeakStage...")
    logger.success("FindPeakStage completed")

    logger.section("Results")
    logger.success("All stages completed successfully")
    logger.scheduler_info(
        "Final statistics",
        total_stages=3,
        total_time="2.5s",
        peaks_found=7,
    )
    logger.separator("=", 80)


def test_different_log_levels() -> None:
    """Test logging at different levels."""
    logger = get_logger(__name__, "levels")

    logger.header("LOG LEVELS TEST")
    logger.debug("DEBUG: Detailed diagnostic information")
    logger.info("INFO: General informational message")
    logger.warning("WARNING: Warning message indicating potential issue")
    logger.error("ERROR: Error message indicating a problem")
    logger.separator()


def test_realistic_workflow() -> None:
    """Test a realistic SAXS processing workflow."""
    scheduler_logger = get_scheduler_logger("saxs.scheduler")
    stage_logger = get_stage_logger("saxs.stage")

    # Start scheduler
    scheduler_logger.header("SAXS PIPELINE EXECUTION")
    scheduler_logger.scheduler_info(
        "Initializing scheduler",
        stages_count=4,
        policy="SaturationInsertPolicy",
    )

    # Simulate pipeline execution
    scheduler_logger.separator("-", 60)
    scheduler_logger.step(1, "Executing CutStage")
    scheduler_logger.scheduler_info(
        "Running stage",
        queue_size=3,
        stage="CutStage",
    )
    stage_logger.stage_info(
        "CutStage",
        "Truncating data",
        cut_point=200,
        original_size=1000,
    )
    scheduler_logger.success("Stage 'CutStage' completed")
    scheduler_logger.scheduler_info(
        "Stage 'CutStage' generated no requests",
    )

    scheduler_logger.separator("-", 60)
    scheduler_logger.step(2, "Executing FilterStage")
    scheduler_logger.scheduler_info(
        "Running stage",
        queue_size=2,
        stage="FilterStage",
    )
    stage_logger.stage_info(
        "FilterStage",
        "Applying smoothing filter",
        window_length=11,
        polyorder=3,
    )
    scheduler_logger.success("Stage 'FilterStage' completed")

    scheduler_logger.separator("-", 60)
    scheduler_logger.step(3, "Executing BackgroundStage")
    stage_logger.stage_info(
        "BackgroundStage",
        "Fitting and subtracting background",
        fit_type="hyperbolic",
    )
    scheduler_logger.success("Stage 'BackgroundStage' completed")

    scheduler_logger.separator("-", 60)
    scheduler_logger.step(4, "Executing FindPeakStage")
    stage_logger.stage_info(
        "FindPeakStage",
        "Peak detection completed",
        data_points=800,
        peaks_found=5,
        intensity_range="[0.12, 4.87]",
    )
    scheduler_logger.success("Stage 'FindPeakStage' completed")
    scheduler_logger.scheduler_info(
        "Stage 'FindPeakStage' generated requests",
        requests_count=1,
    )
    scheduler_logger.scheduler_info(
        "Request APPROVED: ProcessPeakStage",
        queue_size=1,
    )

    scheduler_logger.separator("-", 60)
    scheduler_logger.step(5, "Executing ProcessPeakStage")
    stage_logger.stage_info(
        "ProcessPeakStage",
        "Processing peak",
        peak_index=142,
        peak_height=4.21,
    )
    scheduler_logger.success("Stage 'ProcessPeakStage' completed")

    # Final summary
    scheduler_logger.separator("=", 80)
    scheduler_logger.success("Pipeline execution completed")
    scheduler_logger.scheduler_info(
        "Final state",
        total_steps=5,
    )
    scheduler_logger.separator("=", 80)


def main() -> None:
    """Run all logging tests."""
    # Configure logging with colors enabled
    setup_logging(level=logging.INFO, enable_colors=True)

    print("\n" + "=" * 80)
    print("ENHANCED LOGGING SYSTEM DEMONSTRATION".center(80))
    print("=" * 80 + "\n")

    test_basic_logging()
    print("\n")

    test_component_loggers()
    print("\n")

    test_visual_elements()
    print("\n")

    test_different_log_levels()
    print("\n")

    test_realistic_workflow()
    print("\n")

    print("=" * 80)
    print("TEST COMPLETED".center(80))
    print("=" * 80)


if __name__ == "__main__":
    main()
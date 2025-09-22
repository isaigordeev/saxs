from saxs.saxs.processing.kernels.simple_kernel import SimpleKernel


class TestSimpleKernel:
    """Test cases for Pipeline class using fixtures."""

    def test_simple_kernel_run(self):
        kernel = SimpleKernel()
        kernel.run()

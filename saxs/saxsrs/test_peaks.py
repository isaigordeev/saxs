import time

import numpy as np

import saxsrs


def test_find_peaks_1d() -> None:
    data = np.array([0.0, 1.0, 0.5, 3.0, 0.2, 2.0, 0.1])
    peaks = saxsrs.find_peaks(data)

    assert len(peaks) == 3
    assert peaks[0].index == 1
    assert peaks[1].index == 3
    assert peaks[2].index == 5
    print("1D peaks:", peaks)


def test_find_peaks_filtered():
    data = np.array([0.0, 1.0, 0.5, 3.0, 0.2, 2.0, 0.1])
    peaks = saxsrs.find_peaks(data, min_height=1.5, min_prominence=0.5)

    assert len(peaks) == 2
    assert peaks[0].index == 3
    assert peaks[1].index == 5
    print("Filtered peaks:", peaks)


def test_find_peaks_batch():
    data_2d = np.random.rand(100, 1000)
    data_2d[:, 250] = 5.0
    data_2d[:, 750] = 3.0

    start = time.time()
    batch_peaks = saxsrs.find_peaks_batch(data_2d, min_prominence=1.0)
    elapsed = time.time() - start

    assert len(batch_peaks) == 100
    for row_peaks in batch_peaks:
        indices = [p.index for p in row_peaks]
        assert 250 in indices
        assert 750 in indices

    print(
        f"Batch: {len(batch_peaks)} rows processed in {elapsed * 1000:.2f}ms"
    )
    print(f"First row peaks: {batch_peaks[0]}")


def test_find_max():
    data = np.array([1.0, 5.0, 3.0, 2.0])
    max_val, max_idx = saxsrs.find_max(data)

    assert max_val == 5.0
    assert max_idx == 1
    print(f"find_max: value={max_val}, index={max_idx}")


def test_diff():
    data = np.array([1.0, 3.0, 6.0, 10.0])
    result = saxsrs.diff(data)

    expected = np.array([2.0, 3.0, 4.0])
    np.testing.assert_array_equal(result, expected)
    print(f"diff: {result}")


if __name__ == "__main__":
    test_find_peaks_1d()
    test_find_peaks_filtered()
    test_find_peaks_batch()
    test_find_max()
    test_diff()
    print("\nAll tests passed!")

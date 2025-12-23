use ndarray::Array1;
use numpy::{PyArray1, PyReadonlyArray1, PyReadonlyArray2, ToPyArray};
use pyo3::prelude::*;
use rayon::prelude::*;

/// A detected peak with its properties
#[pyclass]
#[derive(Clone)]
pub struct Peak {
    #[pyo3(get)]
    pub index: usize,
    #[pyo3(get)]
    pub value: f64,
    #[pyo3(get)]
    pub prominence: f64,
}

#[pymethods]
impl Peak {
    fn __repr__(&self) -> String {
        format!(
            "Peak(index={}, value={:.4}, prominence={:.4})",
            self.index, self.value, self.prominence
        )
    }
}

/// Find peaks in 1D array
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     1D array of float64 values
/// min_height : float, optional
///     Minimum peak height (default: -inf)
/// min_prominence : float, optional
///     Minimum prominence (default: 0.0)
///
/// Returns
/// -------
/// list[Peak]
///     List of detected peaks with index, value, and prominence
#[pyfunction]
#[pyo3(signature = (data, min_height=None, min_prominence=None))]
fn find_peaks(
    data: PyReadonlyArray1<f64>,
    min_height: Option<f64>,
    min_prominence: Option<f64>,
) -> Vec<Peak> {
    let slice = data.as_slice().expect("array must be contiguous");
    find_peaks_impl(slice, min_height.unwrap_or(f64::NEG_INFINITY), min_prominence.unwrap_or(0.0))
}

/// Find peaks in each row of 2D array (parallel)
///
/// Parameters
/// ----------
/// data : numpy.ndarray
///     2D array of shape (n_samples, n_points)
/// min_height : float, optional
///     Minimum peak height (default: -inf)
/// min_prominence : float, optional
///     Minimum prominence (default: 0.0)
///
/// Returns
/// -------
/// list[list[Peak]]
///     Peaks for each row
#[pyfunction]
#[pyo3(signature = (data, min_height=None, min_prominence=None))]
fn find_peaks_batch(
    py: Python<'_>,
    data: PyReadonlyArray2<f64>,
    min_height: Option<f64>,
    min_prominence: Option<f64>,
) -> Vec<Vec<Peak>> {
    let array = data.as_array();
    let height = min_height.unwrap_or(f64::NEG_INFINITY);
    let prominence = min_prominence.unwrap_or(0.0);

    // Release GIL for parallel computation
    py.allow_threads(|| {
        array
            .outer_iter()
            .into_iter()
            .collect::<Vec<_>>()
            .into_par_iter()
            .map(|row| {
                let slice = row.as_slice().expect("row must be contiguous");
                find_peaks_impl(slice, height, prominence)
            })
            .collect()
    })
}

/// Core peak finding implementation
fn find_peaks_impl(data: &[f64], min_height: f64, min_prominence: f64) -> Vec<Peak> {
    if data.len() < 3 {
        return Vec::new();
    }

    let mut peaks = Vec::new();

    // Find local maxima
    for i in 1..data.len() - 1 {
        if data[i] > data[i - 1] && data[i] > data[i + 1] && data[i] >= min_height {
            let prominence = calc_prominence(data, i);
            if prominence >= min_prominence {
                peaks.push(Peak {
                    index: i,
                    value: data[i],
                    prominence,
                });
            }
        }
    }

    peaks
}

/// Calculate prominence of a peak
/// Prominence = height above the higher of the two adjacent valleys
fn calc_prominence(data: &[f64], peak_idx: usize) -> f64 {
    let peak_val = data[peak_idx];

    // Find left valley (minimum between start and peak)
    let left_min = data[..peak_idx]
        .iter()
        .copied()
        .fold(f64::INFINITY, f64::min);

    // Find right valley (minimum between peak and end)
    let right_min = data[peak_idx + 1..]
        .iter()
        .copied()
        .fold(f64::INFINITY, f64::min);

    // Prominence is height above the higher valley
    let higher_valley = left_min.max(right_min);
    peak_val - higher_valley
}

/// Find maximum value and index in array
#[pyfunction]
fn find_max(data: PyReadonlyArray1<f64>) -> (f64, usize) {
    let slice = data.as_slice().expect("array must be contiguous");

    let mut max_val = f64::NEG_INFINITY;
    let mut max_idx = 0;

    for (i, &val) in slice.iter().enumerate() {
        if val > max_val {
            max_val = val;
            max_idx = i;
        }
    }

    (max_val, max_idx)
}

/// Compute differences between consecutive elements
#[pyfunction]
fn diff<'py>(py: Python<'py>, data: PyReadonlyArray1<f64>) -> Bound<'py, PyArray1<f64>> {
    let slice = data.as_slice().expect("array must be contiguous");

    let result: Vec<f64> = slice.windows(2).map(|w| w[1] - w[0]).collect();
    let arr = Array1::from_vec(result);

    arr.to_pyarray_bound(py)
}

/// SAXS Rust extension module
#[pymodule]
fn saxsrs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Peak>()?;
    m.add_function(wrap_pyfunction!(find_peaks, m)?)?;
    m.add_function(wrap_pyfunction!(find_peaks_batch, m)?)?;
    m.add_function(wrap_pyfunction!(find_max, m)?)?;
    m.add_function(wrap_pyfunction!(diff, m)?)?;
    Ok(())
}
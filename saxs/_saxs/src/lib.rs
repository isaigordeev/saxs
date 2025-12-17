/// Find maximum value in array, returns (max_value, index)
#[no_mangle]
pub extern "C" fn find_max(data: *const f64, len: usize, out_index: *mut usize) -> f64 {
    if len == 0 {
        return f64::NAN;
    }

    let slice = unsafe { std::slice::from_raw_parts(data, len) };

    let mut max_val = f64::NEG_INFINITY;
    let mut max_idx = 0;

    for (i, &val) in slice.iter().enumerate() {
        if val > max_val {
            max_val = val;
            max_idx = i;
        }
    }

    unsafe {
        *out_index = max_idx;
    }

    max_val
}

/// Compute differences between consecutive elements
/// Writes to `out` buffer and returns pointer to it
#[no_mangle]
pub extern "C" fn calc_diff(data: *const f64, len: usize, out: *mut f64) -> *mut f64 {
    if len < 2 {
        return out;
    }

    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    let out_slice = unsafe { std::slice::from_raw_parts_mut(out, len - 1) };

    for (i, w) in slice.windows(2).enumerate() {
        out_slice[i] = w[1] - w[0];
    }

    out
}

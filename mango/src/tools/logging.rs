use pyo3::prelude::*;
use std::sync::Mutex;
use once_cell::sync::Lazy;

static LOG_CALLBACK: Lazy<Mutex<Option<PyObject>>> = Lazy::new(|| Mutex::new(None));

pub fn set_log_callback(callback: PyObject) {
    let mut cb = LOG_CALLBACK.lock().unwrap_or_else(|e| e.into_inner());
    *cb = Some(callback);
}

pub fn log_to_python(level: &str, msg: &str) {
    let cb_opt = LOG_CALLBACK.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(ref callback) = *cb_opt {
        Python::with_gil(|py| {
            let _ = callback.call1(py, (level, msg));
        });
    } else {
        println!("[RUST-{}] {}", level, msg);
    }
}

// Macros para facilitar el log desde Rust
#[macro_export]
macro_rules! mango_info {
    ($($arg:tt)*) => {
        $crate::tools::logging::log_to_python("INFO", &format!($($arg)*));
    };
}

#[macro_export]
macro_rules! mango_error {
    ($($arg:tt)*) => {
        $crate::tools::logging::log_to_python("ERROR", &format!($($arg)*));
    };
}

#[macro_export]
macro_rules! mango_warn {
    ($($arg:tt)*) => {
        $crate::tools::logging::log_to_python("WARN", &format!($($arg)*));
    };
}

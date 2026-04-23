use gilrs::{Gilrs, Event, Button, Axis};
use pyo3::prelude::*;
use std::thread;
use std::sync::atomic::{AtomicBool, Ordering};

static RUNNING: AtomicBool = AtomicBool::new(false);

/// Inicia el monitoreo de mandos en un hilo de Rust y llama a un callback de Python.
pub fn start_gamepad_monitor(callback: PyObject, py: Python<'_>) {
    if RUNNING.load(Ordering::SeqCst) {
        return;
    }

    RUNNING.store(true, Ordering::SeqCst);
    let callback_clone = callback.clone_ref(py);

    thread::spawn(move || {
        let mut gilrs = match Gilrs::new() {
            Ok(g) => g,
            Err(_) => {
                RUNNING.store(false, Ordering::SeqCst);
                return;
            }
        };

        while RUNNING.load(Ordering::SeqCst) {
            while let Some(Event { id, event, .. }) = gilrs.next_event() {
                let input_key = match event {
                    gilrs::EventType::Connected => {
                        let name = gilrs.gamepad(id).name().to_string();
                        Some(format!("CONNECT:{}", name))
                    },
                    gilrs::EventType::Disconnected => {
                        Some("DISCONNECT".to_string())
                    },
                    gilrs::EventType::ButtonPressed(button, ..) => {
                        match button {
                            Button::South => Some("A".to_string()),
                            Button::East => Some("B".to_string()),
                            Button::North => Some("X".to_string()),
                            Button::West => Some("Y".to_string()),
                            Button::DPadUp => Some("UP".to_string()),
                            Button::DPadDown => Some("DOWN".to_string()),
                            Button::DPadLeft => Some("LEFT".to_string()),
                            Button::DPadRight => Some("RIGHT".to_string()),
                            Button::Start => Some("START".to_string()),
                            Button::Select => Some("SELECT".to_string()),
                            _ => None,
                        }
                    },
                    gilrs::EventType::AxisChanged(axis, val, ..) => {
                        // Deadzone simple para sticks
                        if val.abs() > 0.5 {
                            match axis {
                                Axis::LeftStickX if val > 0.5 => Some("RIGHT".to_string()),
                                Axis::LeftStickX if val < -0.5 => Some("LEFT".to_string()),
                                Axis::LeftStickY if val > 0.5 => Some("UP".to_string()),
                                Axis::LeftStickY if val < -0.5 => Some("DOWN".to_string()),
                                _ => None,
                            }
                        } else {
                            None
                        }
                    },
                    _ => None,
                };

                if let Some(key) = input_key {
                    Python::with_gil(|py| {
                        let _ = callback_clone.call1(py, (key,));
                    });
                }
            }
            thread::sleep(std::time::Duration::from_millis(16)); // ~60fps polling
        }
    });
}

pub fn stop_gamepad_monitor() {
    RUNNING.store(false, Ordering::SeqCst);
}

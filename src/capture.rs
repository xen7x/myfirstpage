use core_graphics::event::{
    CGEvent, CGEventTap, CGEventTapLocation, CGEventTapOptions, CGEventTapPlacement,
    CGEventTapProxy, CGEventType, CallbackResult, EventField
};
use core_foundation::runloop::{CFRunLoop};
use crossbeam_channel::Sender;
use std::sync::{Arc, Mutex};
use crate::overlay::OverlayMessage;
use crate::prediction;
use std::process::Command;

fn simulate_typing(text: &str) {
    let script = format!("tell application \"System Events\" to keystroke \"{}\"", text);
    let _ = Command::new("osascript")
        .arg("-e")
        .arg(script)
        .output();
}

pub fn start_listening(
    input_tx: Sender<String>,
    overlay_tx: Sender<OverlayMessage>,
) {
    let buffer = Arc::new(Mutex::new(String::new()));

    let tap_result = CGEventTap::new(
        CGEventTapLocation::Session,
        CGEventTapPlacement::HeadInsertEventTap,
        CGEventTapOptions::Default,
        vec![CGEventType::KeyDown],
        move |_proxy: CGEventTapProxy, _etype: CGEventType, event: &CGEvent| {
            let keycode = event.get_integer_value_field(EventField::KEYBOARD_EVENT_KEYCODE);

            let char_to_add = match keycode {
                0 => Some('a'),
                1 => Some('s'),
                2 => Some('d'),
                3 => Some('f'),
                4 => Some('h'),
                5 => Some('g'),
                6 => Some('z'),
                7 => Some('x'),
                8 => Some('c'),
                9 => Some('v'),
                11 => Some('b'),
                12 => Some('q'),
                13 => Some('w'),
                14 => Some('e'),
                15 => Some('r'),
                16 => Some('y'),
                17 => Some('t'),
                31 => Some('o'),
                32 => Some('u'),
                34 => Some('i'),
                35 => Some('p'),
                49 => Some(' '),
                _ => None,
            };

            if let Ok(mut buf) = buffer.lock() {
                if keycode == 51 { // backspace
                    if !buf.is_empty() {
                        buf.pop();
                    }
                    let _ = input_tx.send(buf.clone());
                    let _ = overlay_tx.send(OverlayMessage::UpdateInput(buf.clone()));
                    return CallbackResult::Drop; // Drop the backspace
                } else if keycode == 48 { // tab
                    let prediction_suffix = prediction::generate_prediction(&buf);
                    let full_text = format!("{}{}", buf, prediction_suffix);

                    buf.clear();
                    let _ = input_tx.send(buf.clone());
                    let _ = overlay_tx.send(OverlayMessage::UpdateInput(buf.clone()));
                    let _ = overlay_tx.send(OverlayMessage::UpdatePrediction(String::new()));

                    std::thread::spawn(move || {
                        simulate_typing(&full_text);
                    });

                    return CallbackResult::Drop; // Consume the tab key
                } else if let Some(c) = char_to_add {
                    buf.push(c);

                    let _ = input_tx.send(buf.clone());
                    let _ = overlay_tx.send(OverlayMessage::UpdateInput(buf.clone()));
                    return CallbackResult::Drop; // Consume the typing key
                } else {
                    buf.clear();
                    let _ = input_tx.send(buf.clone());
                    let _ = overlay_tx.send(OverlayMessage::UpdateInput(buf.clone()));
                    let _ = overlay_tx.send(OverlayMessage::UpdatePrediction(String::new()));
                }
            }

            CallbackResult::Keep
        },
    );

    match tap_result {
        Ok(tap) => {
            unsafe {
                let loop_source = tap.mach_port().create_runloop_source(0).unwrap();
                CFRunLoop::get_current().add_source(&loop_source, core_foundation::runloop::kCFRunLoopCommonModes);
                tap.enable();
                CFRunLoop::run_current();
            }
        }
        Err(_) => {
            eprintln!("Failed to create event tap. Make sure to run with Accessibility privileges.");
        }
    }
}

use crossbeam_channel::{Receiver, Sender};
use std::thread;
use std::time::Duration;
use crate::overlay::OverlayMessage;

pub fn generate_prediction(input: &str) -> String {
    if input.is_empty() {
        "".to_string()
    } else if input == "o" {
        "hayou gozaimasu".to_string()
    } else if input == "oh" {
        "ayou gozaimasu".to_string()
    } else if input == "oha" {
        "you gozaimasu".to_string()
    } else if input == "ohay" {
        "ou gozaimasu".to_string()
    } else if input == "ohayo" {
        "u gozaimasu".to_string()
    } else if input == "ohayou" {
        " gozaimasu".to_string()
    } else if input.starts_with("a") {
        "rigatou gozaimasu".to_string()
    } else {
        format!(" [{}]", input) // Dummy fallback
    }
}

pub fn start_prediction_worker(
    input_rx: Receiver<String>,
    overlay_tx: Sender<OverlayMessage>,
) {
    thread::spawn(move || {
        while let Ok(input) = input_rx.recv() {
            let prediction = generate_prediction(&input);

            // Simulate AI delay
            thread::sleep(Duration::from_millis(10));
            let _ = overlay_tx.send(OverlayMessage::UpdatePrediction(prediction));
        }
    });
}

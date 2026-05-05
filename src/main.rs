mod capture;
mod overlay;
mod prediction;

use crossbeam_channel::unbounded;
use std::thread;

fn main() {
    let (input_tx, input_rx) = unbounded::<String>();
    let (overlay_tx, overlay_rx) = unbounded::<overlay::OverlayMessage>();

    // Start UI
    let ui_overlay_tx = overlay_tx.clone();

    // Start prediction worker
    prediction::start_prediction_worker(input_rx, overlay_tx);

    // Start capture
    thread::spawn(move || {
        capture::start_listening(input_tx, ui_overlay_tx);
    });

    overlay::start_overlay(overlay_rx);
}

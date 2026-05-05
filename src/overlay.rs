use eframe::egui;
use crossbeam_channel::Receiver;

pub enum OverlayMessage {
    UpdateInput(String),
    UpdatePrediction(String),
}

pub fn start_overlay(rx: Receiver<OverlayMessage>) {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_decorations(false)
            .with_transparent(true)
            .with_always_on_top()
            .with_inner_size([800.0, 100.0]),
        ..Default::default()
    };
    let _ = eframe::run_native(
        "Sovereign Intent Overlay",
        options,
        Box::new(|_cc| Ok(Box::new(OverlayApp::new(rx)))),
    );
}

struct OverlayApp {
    input: String,
    prediction: String,
    rx: Receiver<OverlayMessage>,
}

impl OverlayApp {
    fn new(rx: Receiver<OverlayMessage>) -> Self {
        Self {
            input: String::new(),
            prediction: String::new(),
            rx,
        }
    }
}

impl eframe::App for OverlayApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // Drain messages
        while let Ok(msg) = self.rx.try_recv() {
            match msg {
                OverlayMessage::UpdateInput(s) => self.input = s,
                OverlayMessage::UpdatePrediction(s) => self.prediction = s,
            }
        }

        // Continously redraw to keep checking the channel
        ctx.request_repaint();

        #[allow(deprecated)]
        egui::CentralPanel::default()
            .frame(egui::Frame::NONE.fill(egui::Color32::TRANSPARENT))
            .show(ctx, |ui| {
                ui.horizontal(|ui| {
                    ui.label(
                        egui::RichText::new(&self.input).color(egui::Color32::WHITE).size(32.0)
                    );
                    // Disable spacing between input and prediction
                    ui.spacing_mut().item_spacing.x = 0.0;
                    ui.label(
                        egui::RichText::new(&self.prediction).color(egui::Color32::from_gray(160)).size(32.0)
                    );
                });
            });
    }

    fn ui(&mut self, _ui: &mut egui::Ui, _frame: &mut eframe::Frame) {}
}

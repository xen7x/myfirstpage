# Sovereign Intent MVP (Ghost Text Overlay)

This is a macOS-native MVP for a Ghost Text Overlay application designed to intercept keystrokes, query a fast local AI (mocked) for completion, and allow the user to commit the text with a single keystroke (`Tab`).

## Architecture

* **Language**: Rust
* **Input Interception**: Uses `core-graphics` and `CGEventTap` for global macOS keystroke monitoring.
* **Overlay GUI**: `egui` via `eframe` rendered as a borderless, transparent window atop other windows.
* **Concurrency**: `crossbeam-channel` is used for non-blocking asynchronous communication between the capture, UI, and prediction threads.

## Prerequisites & Building

To compile the application, you need an Apple Silicon target (e.g., `aarch64-apple-darwin`) or Intel target depending on your machine.

1. Ensure you have Rust installed.
2. Build the application natively:
   ```bash
   cargo build --release
   ```

## Running & Accessibility Permissions (TCC)

To run this application, it must intercept global keyboard events via `CGEventTap`. macOS requires strict Accessibility privileges to allow this.

1. Run the application:
   ```bash
   cargo run --release
   ```
   *Note: If you run it from a terminal (e.g., Alacritty, iTerm2, Terminal.app), that terminal must be granted Accessibility permissions.*
2. **Grant Accessibility Privileges**:
   - Open **System Settings** -> **Privacy & Security** -> **Accessibility**.
   - Ensure the toggle next to your Terminal application is enabled.
   - If running a standalone binary outside of a terminal, you may need to add the binary explicitly to the list.
3. If permissions are denied, the program will output an error: `Failed to create event tap. Make sure to run with Accessibility privileges.`

## Usage

* Start typing alphabetic characters. The tool will capture your keystrokes and suppress them from the active application.
* The overlay window will display your input in white and a mock predicted completion in gray.
* Press **Tab** to commit the prediction: the full text (input + prediction) will be simulated via `CGEvent` keyboard events into the currently active application.
* Press **Backspace** to delete characters from your composition buffer.

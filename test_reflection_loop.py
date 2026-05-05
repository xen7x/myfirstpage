import argparse

# MLX specific imports (recommended for Apple Silicon / macOS environments)
# Note: This will only run on an environment where MLX is supported (e.g. Mac/M-series chips).
# For Linux/x86_64, this script will raise an ImportError during `import mlx.core` or `mlx_lm`.
try:
    from mlx_lm import load, generate
except ImportError:
    print("Warning: mlx_lm could not be imported. This script requires an MLX environment to run the Checker.")
    # We continue so the script can at least be inspected, though it will crash if run.

class MockMaker:
    """
    The Maker (Generator) simulating a larger model or agent generating an initial draft.
    """
    def __init__(self):
        self.iteration = 0

    def generate(self, user_prompt, feedback=None):
        self.iteration += 1
        if feedback is None:
            print(f"[Maker] Generating initial draft for: '{user_prompt}'")
            return "Sure, here is your answer: The capital of France is Berlin."
        else:
            print(f"[Maker] Revising draft based on feedback: '{feedback}'")
            # If it failed once, we simulate a corrected output on the second try
            return "The capital of France is Paris."

class Checker:
    """
    The Checker (Auditor) using a lightweight MLX model.
    """
    def __init__(self, model_path="Qwen/Qwen2.5-3B-Instruct"):
        print(f"[Checker] Loading model {model_path} via MLX...")
        self.model, self.tokenizer = load(model_path)
        self.system_prompt = (
            "You are a strict Auditor. Your task is to verify if the provided output accurately "
            "fulfills the user's prompt without any hallucinations, omitted constraints, or logical "
            "contradictions. If you find ANY issues, reply with exactly 'REJECT: [specific reason]'. "
            "If it is flawless, reply with exactly 'APPROVE'."
        )

    def evaluate(self, user_prompt, draft):
        print("[Checker] Evaluating draft...")

        # Format the instruction for the checker
        eval_prompt = (
            f"{self.system_prompt}\n\n"
            f"User Prompt: {user_prompt}\n"
            f"Maker Draft: {draft}\n\n"
            "Verdict:"
        )

        # We construct messages for chat-oriented instruct models
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"User Prompt: {user_prompt}\nMaker Draft: {draft}\n\nVerdict:"}
        ]

        try:
            # Apply chat template
            prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

            # Generate response via MLX
            response = generate(self.model, self.tokenizer, prompt=prompt, max_tokens=100, verbose=False)
            response = response.strip()
            return response
        except Exception as e:
            # Fallback or simple completion if apply_chat_template fails
            prompt = f"<|im_start|>system\n{self.system_prompt}<|im_end|>\n<|im_start|>user\nUser Prompt: {user_prompt}\nMaker Draft: {draft}\n\nVerdict:<|im_end|>\n<|im_start|>assistant\n"
            response = generate(self.model, self.tokenizer, prompt=prompt, max_tokens=100, verbose=False)
            return response.strip()

def run_reflection_loop(user_prompt, max_iterations=3):
    """
    Runs the Maker-Checker reflection loop.
    """
    maker = MockMaker()
    checker = Checker()

    print("="*50)
    print(f"STARTING REFLECTION LOOP (Max Iterations: {max_iterations})")
    print("="*50)

    draft = None
    feedback = None

    for i in range(1, max_iterations + 1):
        print(f"\n--- Iteration {i} ---")

        # 1. Drafting Phase
        draft = maker.generate(user_prompt, feedback)
        print(f"Draft: {draft}")

        # 2. Auditing Phase
        evaluation = checker.evaluate(user_prompt, draft)
        print(f"Checker Evaluation: {evaluation}")

        # 3. Correction Phase
        if evaluation.startswith("APPROVE"):
            print("\n[Loop Terminated] Draft approved by Checker.")
            return draft
        elif evaluation.startswith("REJECT"):
            feedback = evaluation
            print(f"\n[Feedback Sent to Maker] {feedback}")
        else:
            print("\n[Warning] Unexpected Checker format. Assuming REJECT.")
            feedback = f"REJECT: The response format was unexpected: {evaluation}"

    print(f"\n[Loop Terminated] Max iterations ({max_iterations}) reached.")
    return draft

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Sovereign Reflection Loop PoC (MLX)")
    parser.add_argument("--prompt", type=str, default="What is the capital of France?", help="User prompt")
    args = parser.parse_args()

    final_output = run_reflection_loop(args.prompt)

    print("="*50)
    print("FINAL OUTPUT:")
    print(final_output)
    print("="*50)

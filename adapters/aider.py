import subprocess, json, tempfile, os

class AiderAdapter:
    def __init__(self, binary="aider"):
        self.binary = binary

    def propose(self, goal, files):
        # Provide goal + restricted file list to Aider
        prompt = f"Task: {goal}\nFocus on files: {', '.join(files)}"
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(prompt)
            path = f.name
        # Example run - in practice you'd use Aider chat mode with --message
        cmd = [self.binary, "--message-file", path] + files
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        return {"stdout": proc.stdout, "stderr": proc.stderr, "rc": proc.returncode}
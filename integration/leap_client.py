import os, time, json, logging, requests
from typing import List, Dict, Optional

log = logging.getLogger("leap")

class LeapClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.leap.new/v1"):
        self.api_key = api_key or os.getenv("LEAP_API_KEY")
        if not self.api_key:
            raise ValueError("LEAP_API_KEY missing")
        self.base_url = base_url.rstrip("/")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def embed(self, texts: List[str], model: str = "embed-v1") -> List[List[float]]:
        resp = requests.post(f"{self.base_url}/embeddings",
                             headers=self._headers(),
                             json={"model": model, "input": texts})
        resp.raise_for_status()
        data = resp.json()
        return [d["embedding"] for d in data["data"]]

    def summarize(self, text: str, model: str = "utility-llm") -> str:
        prompt = f"Summarize succinctly:\n{text}"
        resp = requests.post(f"{self.base_url}/chat/completions",
                             headers=self._headers(),
                             json={"model": model, "messages":[{"role":"user","content":prompt}]})
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def generate_image(self, prompt: str, model: str = "image-gen-v2", size: str = "1024x1024") -> Dict:
        resp = requests.post(f"{self.base_url}/images/generations",
                             headers=self._headers(),
                             json={"model": model, "prompt": prompt, "size": size})
        resp.raise_for_status()
        return resp.json()

    def fine_tune(self, model: str, training_file: str, suffix: str) -> str:
        # training_file should already be uploaded if API requires multi-step; simplified placeholder
        resp = requests.post(f"{self.base_url}/fine_tunes",
                             headers=self._headers(),
                             json={"model": model, "training_file": training_file, "suffix": suffix})
        resp.raise_for_status()
        job = resp.json()
        return job["id"]

    def fine_tune_status(self, job_id: str) -> Dict:
        resp = requests.get(f"{self.base_url}/fine_tunes/{job_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()
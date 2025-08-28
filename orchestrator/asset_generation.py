import os, json, logging
from typing import Dict
from integration.leap_client import LeapClient
from .prompt_sanitizer import sanitize_for_asset
log = logging.getLogger("asset_gen")

class AssetGenerator:
    def __init__(self, output_dir: str, leap_client: LeapClient, policy: Dict):
        self.out = output_dir
        os.makedirs(self.out, exist_ok=True)
        self.client = leap_client
        self.policy = policy

    def generate_feature_icon(self, description: str, task_meta: Dict, confidential: bool):
        if confidential and self.policy.get("deny_external_asset_on_confidential"):
            raise RuntimeError("External asset generation blocked by policy.")
        clean_prompt = sanitize_for_asset(description)
        data = self.client.generate_image(
            prompt=f"Minimalistic vector friendly icon for: {clean_prompt}",
            model="image-gen-v2", size="512x512"
        )
        image_url = data["data"][0]["url"] if "data" in data else None
        record = {"prompt": clean_prompt, "image_url": image_url, "task": task_meta.get("id")}
        with open(os.path.join(self.out, f"asset_{task_meta.get('id')}.json"), "w") as f:
            json.dump(record, f, indent=2)
        return record
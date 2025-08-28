import yaml, logging
from typing import Dict, Any

log = logging.getLogger("model_router")

class ModelRouter:
    def __init__(self, routing_path: str):
        with open(routing_path, "r") as f:
            self.config = yaml.safe_load(f)

    def select(self, strategy: str):
        strat = self.config["strategies"].get(strategy)
        if not strat:
            return {"provider":"coddellm","model":self.config["default_model"]}
        if "primary" in strat:
            provider, model = self._split(strat["primary"])
            return {"provider":provider, "model":model}
        if "chain" in strat:
            chain = []
            for step in strat["chain"]:
                provider, model = self._split(step["provider"]), step.get("model")
                if isinstance(provider, tuple):
                    provider = provider[0]  # when provider already embed model
                chain.append({"provider":step["provider"], "model":model, "role":step.get("role")})
            return {"chain": chain}
        return {"provider":"coddellm","model":self.config["default_model"]}

    def _split(self, s: str):
        if ":" in s:
            return tuple(s.split(":",1))
        return (s, "")

    def is_leap(self, provider: str):
        return provider.startswith("leap")

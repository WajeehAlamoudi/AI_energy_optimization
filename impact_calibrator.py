import random

import pandas as pd
import json
from pathlib import Path
import numpy as np
from paths import DATA_DIR


class ImpactCalibrator:
    def __init__(self, catalog_path= DATA_DIR / "devices_catalog.json", output_path= DATA_DIR / "impact_map.json"):
        self.catalog_path = Path(catalog_path)
        self.output_path = Path(output_path)

        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Device catalog not found at {self.catalog_path}")

        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.devices = json.load(f)

    def calibrate(self):
        """
        Automatically generates impact factors for every permission keyword
        found in the current devices_catalog.json.
        """
        # 🔍 Collect all unique permission keywords
        keywords = set()
        for device, info in self.devices.items():
            for perm in info.get("permissions", []):
                # split by underscores or hyphens for better matching
                parts = [p for p in perm.replace("-", "_").split("_") if p]
                keywords.update(parts)

        # 🧮 Build energy/temperature impact map
        impact_map = {}
        for key in keywords:
            key_lower = key.lower()
            factor = 1.0
            temp_change = 0.0

            # Simple heuristic based on keyword meaning
            if "eco" in key_lower or "save" in key_lower:
                factor = random.uniform(0.6, 0.8)
                temp_change = random.uniform(-0.1, -0.05)
            elif "low" in key_lower:
                factor = random.uniform(0.75, 0.9)
                temp_change = random.uniform(-0.3, -0.1)
            elif "medium" in key_lower:
                factor = random.uniform(0.95, 1.05)
                temp_change = random.uniform(-0.1, 0.1)
            elif "high" in key_lower:
                factor = random.uniform(1.1, 1.3)
                temp_change = random.uniform(0.1, 0.3)
            elif "off" in key_lower:
                factor = random.uniform(0.02, 0.1)
                temp_change = 0.0
            elif "on" in key_lower:
                factor = 1.0
                temp_change = 0.0
            elif "auto" in key_lower or "standard" in key_lower:
                factor = 1.0
                temp_change = 0.0
            elif "charge" in key_lower:
                factor = random.uniform(1.2, 1.4)
                temp_change = 0.0
            elif "cool" in key_lower:
                factor = random.uniform(1.1, 1.3)
                temp_change = random.uniform(-0.3, -0.1)
            elif "heat" in key_lower or "warm" in key_lower:
                factor = random.uniform(1.2, 1.5)
                temp_change = random.uniform(0.1, 0.4)
            elif "dim" in key_lower:
                factor = random.uniform(0.7, 0.9)
                temp_change = 0.0

            impact_map[key_lower] = {
                "energy_factor": round(factor, 3),
                "temp_change": round(temp_change, 3)
            }

        # 💾 Save the new impact map
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(impact_map, f, indent=2, ensure_ascii=False)

        print(f"Impact map auto-generated from {len(keywords)} permission keywords.")
        return impact_map

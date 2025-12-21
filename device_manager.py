import json
from pathlib import Path
from paths import DATA_DIR
from impact_calibrator import ImpactCalibrator


class DeviceManager:
    """Handles device catalog and keeps impact map synced."""

    def __init__(self, catalog_path=None):
        # Notes:
        # - Loads device catalog from JSON file under DATA_DIR
        # - Ensures folder exists before reading/writing
        self.catalog_path = Path(catalog_path or DATA_DIR / "devices_catalog.json")
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.devices = {}
        self.devices = self.load_devices()

    #  JSON
    def load_devices(self):
        """Load existing catalog safely without overwriting valid files."""
        # Notes:
        # - If file missing: create empty catalog file
        # - If file empty or JSON broken: return empty dict without touching the file
        if not self.catalog_path.exists():
            print(f"[WARN] | devices_catalog.json not found, creating a new one.")
            self.save_devices({})
            return {}

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    print(f"[WARN] | devices_catalog.json is empty — please re-add your data manually.")
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"[WARN] | JSON error: {e}. Keeping existing file unchanged.")
            return {}

    def save_devices(self, data=None):
        # Notes:
        # - Writes either the provided data or the current in-memory devices dict
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(data or self.devices, f, indent=2, ensure_ascii=False)

    #  Operations
    def get_all_devices(self):
        # Notes:
        # - Returns full device catalog as dict
        return self.devices

    def add_device(self, name, base_kWh, permissions=None):
        # Notes:
        # - Adds a new device with base_kWh + permissions list
        # - Triggers impact map recalibration after save
        name = name.strip().title()
        if name in self.devices:
            return {"error": f"{name} already exists."}
        self.devices[name] = {"base_kWh": base_kWh, "permissions": permissions or []}
        self.save_devices()
        self._auto_recalibrate()
        return {"message": f"{name} added successfully."}

    def update_device(self, name, base_kWh=None, permissions=None):
        # Notes:
        # - Updates base_kWh and/or permissions for an existing device
        # - Triggers impact map recalibration after save
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        if base_kWh is not None:
            self.devices[name]["base_kWh"] = base_kWh
        if permissions is not None:
            self.devices[name]["permissions"] = permissions
        self.save_devices()
        self._auto_recalibrate()
        return {"message": f"{name} updated successfully."}

    def remove_device(self, name):
        # Notes:
        # - Removes device from catalog and recalibrates impact map
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        del self.devices[name]
        self.save_devices()
        self._auto_recalibrate()
        return {"message": f"{name} deleted successfully."}

    #  Permissions
    def add_permission(self, name, permission):
        # Notes:
        # - Adds permission string if not already present
        # - Recalibrates impact map after change
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        if permission not in self.devices[name]["permissions"]:
            self.devices[name]["permissions"].append(permission)
            self.save_devices()
            self._auto_recalibrate()
            return {"message": f"Permission '{permission}' added to {name}."}
        return {"warning": f"Permission '{permission}' already exists for {name}."}

    def remove_permission(self, name, permission):
        # Notes:
        # - Removes permission string if present
        # - Recalibrates impact map after change
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        if permission in self.devices[name]["permissions"]:
            self.devices[name]["permissions"].remove(permission)
            self.save_devices()
            self._auto_recalibrate()
            return {"message": f"Permission '{permission}' removed from {name}."}
        return {"error": f"Permission '{permission}' not found in {name}."}

    #  Helpers
    def _auto_recalibrate(self):
        # - Rebuilds/updates the impact map whenever catalog changes
        try:
            print(f"[INFO] | Auto-recalibrating impact map...")
            calibrator = ImpactCalibrator()
            calibrator.calibrate()
            print(f"[INFO] | Impact map updated.")
        except Exception as e:
            print(f"[WARN] | Recalibration failed: {e}")

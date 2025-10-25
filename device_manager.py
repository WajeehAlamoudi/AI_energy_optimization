import json
from pathlib import Path

from impact_calibrator import ImpactCalibrator

DATA_PATH = Path("data/devices_catalog.json")

"""
Action	HTTP Method	Example Route
Get all devices	GET	/devices
Add new device	POST	/devices/add
Update device	PUT	/devices/update/{name}
Delete device	DELETE	/devices/{name}
Manage permissions	POST / DELETE	/devices/{name}/permissions
"""


class DeviceManager:
    def __init__(self):
        self.devices = self.load_devices()

    # ---------- Core JSON Handling ----------
    def load_devices(self):
        if not DATA_PATH.exists():
            print("⚠️ devices_catalog.json not found, creating a new one.")
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.save_devices({})
            return {}
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_devices(self, data=None):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data or self.devices, f, indent=2, ensure_ascii=False)

    # ---------- Device Operations ----------
    def get_all_devices(self):
        return self.devices

    def add_device(self, name, base_kWh, permissions=None):
        name = name.strip().title()
        if name in self.devices:
            return {"error": f"{name} already exists."}
        self.devices[name] = {
            "base_kWh": base_kWh,
            "permissions": permissions or []
        }
        self.save_devices()
        return {"message": f"{name} added successfully."}

    def update_device(self, name, base_kWh=None, permissions=None):
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        if base_kWh is not None:
            self.devices[name]["base_kWh"] = base_kWh
        if permissions is not None:
            self.devices[name]["permissions"] = permissions
        self.save_devices()
        return {"message": f"{name} updated successfully."}

    def remove_device(self, name):
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        del self.devices[name]
        self.save_devices()
        return {"message": f"{name} deleted successfully."}

    # ---------- Permission Management ----------
    def get_permissions(self, name):
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        return self.devices[name]["permissions"]

    def add_permission(self, name, permission):
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}

        if permission not in self.devices[name]["permissions"]:
            self.devices[name]["permissions"].append(permission)
            self.save_devices()

            # 🔄 Automatically update the impact map whenever a new permission is added
            calibrator = ImpactCalibrator()
            calibrator.calibrate()

        return {"message": f"Permission '{permission}' added to {name}."}

    def remove_permission(self, name, permission):
        name = name.strip().title()
        if name not in self.devices:
            return {"error": f"{name} not found."}
        if permission in self.devices[name]["permissions"]:
            self.devices[name]["permissions"].remove(permission)
            self.save_devices()
            return {"message": f"Permission '{permission}' removed from {name}."}
        return {"error": f"Permission '{permission}' not found in {name}."}

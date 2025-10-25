import json
from pathlib import Path
from device_manager import DeviceManager


class HomeManager:
    def __init__(self, homes_path="/data/homes.json"):
        self.homes_path = Path(homes_path)
        self.homes_path.parent.mkdir(parents=True, exist_ok=True)  # ✅ auto-create /data/
        self.device_manager = DeviceManager()
        self.homes = self._load_homes()

    # ---------- Load & Save ----------
    def _load_homes(self):
        if self.homes_path.exists():
            with open(self.homes_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_homes(self):
        with open(self.homes_path, "w", encoding="utf-8") as f:
            json.dump(self.homes, f, indent=2, ensure_ascii=False)

    # ---------- Home management ----------
    def add_home(self, home_name, comfort_range=(21, 25)):
        home_name = home_name.strip().title()
        if home_name not in self.homes:
            self.homes[home_name] = {"comfort_range": comfort_range, "rooms": {}}
            self._save_homes()
            return {"message": f"🏡 Home '{home_name}' added successfully."}
        return {"error": f"Home '{home_name}' already exists."}

    def delete_home(self, home_name):
        home_name = home_name.strip().title()
        if home_name in self.homes:
            del self.homes[home_name]
            self._save_homes()
            return {"message": f"🏠 Home '{home_name}' removed."}
        return {"error": f"Home '{home_name}' not found."}

    # ---------- Room management ----------
    def add_room(self, home_name, room_name):
        home_name, room_name = home_name.strip().title(), room_name.strip().title()
        if home_name not in self.homes:
            return {"error": f"Home '{home_name}' not found."}
        if room_name in self.homes[home_name]["rooms"]:
            return {"error": f"Room '{room_name}' already exists in '{home_name}'."}

        self.homes[home_name]["rooms"][room_name] = {"devices": []}
        self._save_homes()
        return {"message": f"🛋️ Room '{room_name}' added to '{home_name}'."}

    def rename_room(self, home_name, old_name, new_name):
        home_name = home_name.strip().title()
        old_name = old_name.strip().title()
        new_name = new_name.strip().title()

        if home_name not in self.homes:
            return {"error": f"Home '{home_name}' not found."}

        rooms = self.homes[home_name]["rooms"]
        if old_name not in rooms:
            return {"error": f"Room '{old_name}' not found in '{home_name}'."}
        if new_name in rooms:
            return {"error": f"Room '{new_name}' already exists in '{home_name}'."}

        rooms[new_name] = rooms.pop(old_name)
        self._save_homes()
        return {"message": f"✅ Room renamed from '{old_name}' → '{new_name}' in '{home_name}'."}

    def delete_room(self, home_name, room_name):
        home_name, room_name = home_name.strip().title(), room_name.strip().title()
        if home_name not in self.homes:
            return {"error": f"Home '{home_name}' not found."}
        if room_name not in self.homes[home_name]["rooms"]:
            return {"error": f"Room '{room_name}' not found."}

        del self.homes[home_name]["rooms"][room_name]
        self._save_homes()
        return {"message": f"🗑️ Room '{room_name}' deleted from '{home_name}'."}

    def assign_device(self, home_name, room_name, device_name):
        home_name, room_name, device_name = (
            home_name.strip().title(),
            room_name.strip().title(),
            device_name.strip().title(),
        )

        if home_name not in self.homes:
            return {"error": f"Home '{home_name}' not found."}
        if room_name not in self.homes[home_name]["rooms"]:
            return {"error": f"Room '{room_name}' not found in '{home_name}'."}
        if device_name not in self.device_manager.get_all_devices():
            return {"error": f"Device '{device_name}' not found in catalog."}

        room_devices = self.homes[home_name]["rooms"][room_name]["devices"]
        if device_name not in room_devices:
            room_devices.append(device_name)
            self._save_homes()
            return {"message": f"Device '{device_name}' added to '{room_name}' in '{home_name}'."}
        return {"warning": f"Device '{device_name}' already in '{room_name}'."}

    def get_home_devices(self, home_name):
        home_name = home_name.strip().title()
        if home_name not in self.homes:
            return {"error": f"Home '{home_name}' not found."}
        all_devices = []
        for room in self.homes[home_name]["rooms"].values():
            all_devices.extend(room.get("devices", []))
        return list(set(all_devices))

"""
🧪 Test: HomeManager — Home, Room, and Device assignment checks
"""

from home_manager import HomeManager
from pathlib import Path
from pprint import pprint

print("=== 🏡 STEP 1: INITIALIZE HOME MANAGER ===")
manager = HomeManager()
print("Homes file path:", manager.homes_path)
print("Existing homes:", list(manager.homes.keys()), "\n")

# 🧹 Reset before testing (optional safety)
if "Villa 12" in manager.homes:
    print(manager.delete_home("Villa 12"))

# ------------------------------------------------------------
# STEP 2️⃣: Add a home and rooms
# ------------------------------------------------------------
print("\n=== 🏠 STEP 2: ADD HOME & ROOMS ===")
print(manager.add_home("Villa 12", comfort_range=(22, 26)))
print(manager.add_room("Villa 12", "Living Room"))
print(manager.add_room("Villa 12", "Kitchen"))
print(manager.rename_room("Villa 12", "Kitchen", "Main Kitchen"))

# ------------------------------------------------------------
# STEP 3️⃣: Assign devices
# ------------------------------------------------------------
print("\n=== 🔌 STEP 3: ASSIGN DEVICES TO ROOMS ===")
print(manager.assign_device("Villa 12", "Living Room", "Air Conditioning"))
print(manager.assign_device("Villa 12", "Living Room", "Tv"))
print(manager.assign_device("Villa 12", "Main Kitchen", "Fridge"))
print(manager.assign_device("Villa 12", "Main Kitchen", "Oven"))

# ------------------------------------------------------------
# STEP 4️⃣: Duplicate assignment check
# ------------------------------------------------------------
print("\n=== ⚠️ STEP 4: DUPLICATE DEVICE TEST ===")
print(manager.assign_device("Villa 12", "Living Room", "Tv"))

# ------------------------------------------------------------
# STEP 5️⃣: Fetch and inspect
# ------------------------------------------------------------
print("\n=== 🧾 STEP 5: STRUCTURE VALIDATION ===")
pprint(manager.homes["Villa 12"])
print("\nDevices in Villa 12:", manager.get_home_devices("Villa 12"))

# ------------------------------------------------------------
# STEP 6️⃣: Cleanup (optional)
# ------------------------------------------------------------
# print(manager.delete_home("Villa 12"))

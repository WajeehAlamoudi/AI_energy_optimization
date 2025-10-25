from device_manager import DeviceManager


class EnergyOptimizer:
    def __init__(self, comfort_range=(21, 25)):
        self.manager = DeviceManager()
        self.comfort_min, self.comfort_max = comfort_range

    def optimize(self, predicted_kWh, predicted_temp, user_prefs=None):
        """
        Simple rule-based optimizer that decides which devices to adjust
        to reduce energy use while maintaining comfort.
        """
        recommendations = []
        devices = self.manager.get_all_devices()

        # Example rules
        if predicted_kWh > 4.0:
            # 1️⃣ Suggest eco modes for high-consumption devices
            for name, info in devices.items():
                if info["base_kWh"] > 1.0 and "eco_mode" in info["permissions"]:
                    recommendations.append({
                        "device": name,
                        "action": "eco_mode",
                        "expected_saving": round(info["base_kWh"] * 0.2, 3)
                    })

        # 2️⃣ Adjust temperature-related devices
        if predicted_temp > self.comfort_max:
            recommendations.append({
                "device": "Air Conditioning",
                "action": "set_low",
                "note": "Reduce indoor temp to maintain comfort"
            })
        elif predicted_temp < self.comfort_min:
            recommendations.append({
                "device": "Heater",
                "action": "set_low",
                "note": "Increase temp slightly to save energy"
            })

        # 3️⃣ Fallback if nothing to do
        if not recommendations:
            recommendations.append({
                "device": "None",
                "action": "keep_current_settings",
                "note": "System is within optimal conditions"
            })

        total_saving = sum(r.get("expected_saving", 0) for r in recommendations)
        return {
            "predicted_kWh": predicted_kWh,
            "predicted_temp": predicted_temp,
            "recommended_actions": recommendations,
            "estimated_kWh_saving": round(total_saving, 3)
        }

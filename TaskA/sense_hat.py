# sense_hat.py (fake module for testing)

import random

class SenseHat:
    def __init__(self):
        self._messages = []

    def get_temperature(self) -> float:
        # fake ~20-30 °C
        return round(random.uniform(18.0, 32.0), 2)

    def get_humidity(self) -> float:
        # fake ~30-70 %
        return round(random.uniform(30.0, 70.0), 2)

    def get_pressure(self) -> float:
        # fake ~950–1050 hPa
        return round(random.uniform(950.0, 1050.0), 2)

    def get_orientation(self) -> dict:
        # fake pitch/roll/yaw in degrees
        return {
            "pitch": round(random.uniform(-180.0, 180.0), 2),
            "roll":  round(random.uniform(-180.0, 180.0), 2),
            "yaw":   round(random.uniform(-180.0, 180.0), 2)
        }

    def show_message(self, text_string: str, scroll_speed: float = 0.1, back_colour=None):
        # just print to console instead of displaying
        self._messages.append((text_string, back_colour))
        print(f"[FAKE DISPLAY] {text_string} (colour={back_colour})")

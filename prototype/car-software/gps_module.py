import time
import random

class GPSSimulator:
    def __init__(self, start_lat=12.9716, start_lon=77.5946):
        """
        Initializes the GPS simulator.
        :param start_lat: Starting latitude (default: Bangalore)
        :param start_lon: Starting longitude (default: Bangalore)
        """
        self.lat = start_lat
        self.lon = start_lon
        self.speed_mps = 15 # meters per second (approx 54 km/h)
        self.last_update = time.time()

    def get_location(self):
        """
        Simulates getting the current GPS location.
        The location changes based on a constant speed and a slightly randomized direction.
        """
        current_time = time.time()
        time_delta = current_time - self.last_update

        # Move in a generally north-easterly direction with some randomness
        direction = random.uniform(0, 0.5) # Radians
        distance = self.speed_mps * time_delta

        # Simple approximation for lat/lon change
        delta_lat = distance * 0.000009 * random.uniform(0.8, 1.2) # ~1m in degrees
        delta_lon = distance * 0.000009 * random.uniform(0.8, 1.2) # ~1m in degrees

        self.lat += delta_lat
        self.lon += delta_lon

        self.last_update = current_time

        return {
            "latitude": self.lat,
            "longitude": self.lon,
            "timestamp": int(current_time)
        }

if __name__ == '__main__':
    # Example usage
    gps = GPSSimulator()
    for _ in range(10):
        print(gps.get_location())
        time.sleep(1)

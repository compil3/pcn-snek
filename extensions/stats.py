import asyncio
import time
from extensions import globals



def stats():    
    while True:
        time.sleep(5)
        globals.time_seconds += 5
        if globals.time_seconds == 60:
            globals.time_seconds = 0
            globals.time_minutes += 1
            if globals.time_minutes == 60:
                globals.time_minutes = 0
                globals.time_hours += 1
                if globals.time_hours == 24:
                    globals.time_hours = 0
                    globals.time_days += 1
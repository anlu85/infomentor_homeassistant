from homeassistant.helpers.entity import Entity
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .const import DOMAIN, LOCAL_TZ

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = []
    for day_offset, day_name in [(0, "Today"), (1, "Tomorrow")]:
        sensors += [
            # Registered times
            InfomentorRegisteredStartDatetimeSensor(coordinator, day_offset, day_name),
            InfomentorRegisteredStartTimeSensor(coordinator, day_offset, day_name),
            InfomentorRegisteredEndDatetimeSensor(coordinator, day_offset, day_name),
            InfomentorRegisteredEndTimeSensor(coordinator, day_offset, day_name),
            # School times
            InfomentorSchoolStartDatetimeSensor(coordinator, day_offset, day_name),
            InfomentorSchoolStartTimeSensor(coordinator, day_offset, day_name),
            InfomentorSchoolEndDatetimeSensor(coordinator, day_offset, day_name),
            InfomentorSchoolEndTimeSensor(coordinator, day_offset, day_name),
        ]
    async_add_entities(sensors, True)

def _get_day_data(coordinator, day_offset):
    data = coordinator.data.get("time_registrations", {})
    days = data.get("days", [])
    target_date = (datetime.now(LOCAL_TZ) + timedelta(days=day_offset)).date()
    for day in days:
        day_date = datetime.fromisoformat(day["date"]).date()
        if day_date == target_date:
            return day
    return None

# --- Registered times ---

class InfomentorRegisteredStartDatetimeSensor(Entity):
    _attr_device_class = "timestamp"
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor Registered Start Datetime {day_name}"

    @property
    def state(self):
        day = _get_day_data(self.coordinator, self.day_offset)
        if day and day.get("startDateTime"):
            dt = datetime.fromisoformat(day["startDateTime"]).replace(tzinfo=LOCAL_TZ)
            return dt.isoformat()
        return None

class InfomentorRegisteredStartTimeSensor(Entity):
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor Registered Start Time {day_name}"

    @property
    def state(self):
        day = _get_day_data(self.coordinator, self.day_offset)
        if day and day.get("startDateTime"):
            dt = datetime.fromisoformat(day["startDateTime"]).replace(tzinfo=LOCAL_TZ)
            return dt.strftime("%H:%M")
        return None

class InfomentorRegisteredEndDatetimeSensor(Entity):
    _attr_device_class = "timestamp"
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor Registered End Datetime {day_name}"

    @property
    def state(self):
        day = _get_day_data(self.coordinator, self.day_offset)
        if day and day.get("endDateTime"):
            dt = datetime.fromisoformat(day["endDateTime"]).replace(tzinfo=LOCAL_TZ)
            return dt.isoformat()
        return None

class InfomentorRegisteredEndTimeSensor(Entity):
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor Registered End Time {day_name}"

    @property
    def state(self):
        day = _get_day_data(self.coordinator, self.day_offset)
        if day and day.get("endDateTime"):
            dt = datetime.fromisoformat(day["endDateTime"]).replace(tzinfo=LOCAL_TZ)
            return dt.strftime("%H:%M")
        return None

# --- School times ---

class InfomentorSchoolStartDatetimeSensor(Entity):
    _attr_device_class = "timestamp"
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor School Start Datetime {day_name}"

    @property
    def state(self):
        events = self.coordinator.data.get("timetable", [])
        target_date = (datetime.now(LOCAL_TZ) + timedelta(days=self.day_offset)).date()
        events_today = [
            ev for ev in events
            if datetime.fromisoformat(ev["start"]).replace(tzinfo=LOCAL_TZ).date() == target_date
        ]
        if events_today:
            first_event = min(events_today, key=lambda ev: ev["start"])
            dt = datetime.fromisoformat(first_event["start"]).replace(tzinfo=LOCAL_TZ)
            return dt.isoformat()
        return None

class InfomentorSchoolStartTimeSensor(Entity):
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor School Start Time {day_name}"

    @property
    def state(self):
        events = self.coordinator.data.get("timetable", [])
        target_date = (datetime.now(LOCAL_TZ) + timedelta(days=self.day_offset)).date()
        events_today = [
            ev for ev in events
            if datetime.fromisoformat(ev["start"]).replace(tzinfo=LOCAL_TZ).date() == target_date
        ]
        if events_today:
            first_event = min(events_today, key=lambda ev: ev["start"])
            return first_event["start"][11:16]  # HH:MM
        return None

class InfomentorSchoolEndDatetimeSensor(Entity):
    _attr_device_class = "timestamp"
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor School End Datetime {day_name}"

    @property
    def state(self):
        events = self.coordinator.data.get("timetable", [])
        target_date = (datetime.now(LOCAL_TZ) + timedelta(days=self.day_offset)).date()
        events_today = [
            ev for ev in events
            if datetime.fromisoformat(ev["end"]).replace(tzinfo=LOCAL_TZ).date() == target_date
        ]
        if events_today:
            last_event = max(events_today, key=lambda ev: ev["end"])
            dt = datetime.fromisoformat(last_event["end"]).replace(tzinfo=LOCAL_TZ)
            return dt.isoformat()
        return None

class InfomentorSchoolEndTimeSensor(Entity):
    def __init__(self, coordinator, day_offset, day_name):
        self.coordinator = coordinator
        self.day_offset = day_offset
        self._attr_name = f"Infomentor School End Time {day_name}"

    @property
    def state(self):
        events = self.coordinator.data.get("timetable", [])
        target_date = (datetime.now(LOCAL_TZ) + timedelta(days=self.day_offset)).date()
        events_today = [
            ev for ev in events
            if datetime.fromisoformat(ev["end"]).replace(tzinfo=LOCAL_TZ).date() == target_date
        ]
        if events_today:
            last_event = max(events_today, key=lambda ev: ev["end"])
            return last_event["end"][11:16]  # HH:MM
        return None
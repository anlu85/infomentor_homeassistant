from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from .const import DOMAIN, LOCAL_TZ

from datetime import datetime
from zoneinfo import ZoneInfo

# async def async_setup_entry(hass, entry, async_add_entities):
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     async_add_entities([InfomentorTimeRegistrationCalendar(coordinator)], True)

class InfomentorTimeRegistrationCalendar(CalendarEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Time Registration"
        self._attr_unique_id = "time_registration" 

    @property
    def event(self):
        now = datetime.now(LOCAL_TZ)
        events = self._get_events()
        future_events = [ev for ev in events if ev.start > now]
        if future_events:
            return min(future_events, key=lambda ev: ev.start)
        return None

    async def async_get_events(self, hass, start_date, end_date):
        return [
            ev for ev in self._get_events()
            if ev.end >= start_date and ev.start <= end_date
        ]

    def _get_events(self):
        data = self.coordinator.data.get("time_registrations", {})
        days = data.get("days", [])
        events = []
        for day in days:
            # Skip if no registration
            if not day.get("startDateTime") or not day.get("endDateTime"):
                continue
            start = datetime.fromisoformat(day["startDateTime"]).replace(tzinfo=LOCAL_TZ)
            end = datetime.fromisoformat(day["endDateTime"]).replace(tzinfo=LOCAL_TZ)
            summary = "On Leave" if day.get("onLeave") else "Fritids"
            if day.get("isSchoolClosed"):
                summary = "School Closed"
            events.append(CalendarEvent(
                summary=summary,
                start=start,
                end=end,
                description=self._make_description(day),
                location=""
            ))
        return events

    def _make_description(self, day):
        desc = []
        if day.get("isLocked"):
            desc.append("Locked")
        if day.get("canEdit"):
            desc.append("Editable")
        if day.get("schoolClosedReason"):
            desc.append(f"Closed: {day['schoolClosedReason']}")
        if day.get("schoolOpeningTime") and day.get("schoolClosingTime"):
            desc.append(f"School open: {day['schoolOpeningTime'][11:16]}–{day['schoolClosingTime'][11:16]}")
        return ", ".join(desc)
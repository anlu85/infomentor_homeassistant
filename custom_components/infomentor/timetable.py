from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from .const import DOMAIN, LOCAL_TZ

from datetime import datetime
from zoneinfo import ZoneInfo

# async def async_setup_entry(hass, entry, async_add_entities):
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     async_add_entities([InfomentorTimetable(coordinator)], True)

class InfomentorTimetableCalender(CalendarEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "Timetable"
        self._attr_unique_id = "timetable"

    @property
    def event(self):
        from datetime import datetime
        now = datetime.now()
        events = self.coordinator.data.get("timetable", [])
        future_events = [
            ev for ev in events
            if datetime.fromisoformat(ev["start"]) > now
        ]
        if future_events:
            next_ev = min(future_events, key=lambda ev: ev["start"])
            return self._event_to_hass(next_ev)
        return None

    async def async_get_events(self, hass, start_date, end_date):
        return [
            self._event_to_hass(ev)
            for ev in self.coordinator.data.get("timetable", [])
            if self._event_in_range(ev, start_date, end_date)
        ]

    def _event_in_range(self, ev, start, end):
        ev_start = datetime.fromisoformat(ev["start"]).replace(tzinfo=LOCAL_TZ)
        ev_end = datetime.fromisoformat(ev["end"]).replace(tzinfo=LOCAL_TZ)
        # Make start/end timezone-aware if they are naive
        if start.tzinfo is None:
            start = start.replace(tzinfo=LOCAL_TZ)
        if end.tzinfo is None:
            end = end.replace(tzinfo=LOCAL_TZ)
        return ev_end >= start and ev_start <= end

    def _event_to_hass(self, ev):
        def to_local(dtstr):
            # Parse naive datetime string and attach local timezone
            dt = datetime.fromisoformat(dtstr)
            return dt.replace(tzinfo=LOCAL_TZ)
        return CalendarEvent(
            summary=ev["title"],
            start=to_local(ev["start"]),
            end=to_local(ev["end"]),
            description=self._make_description(ev),
            location=ev["notes"].get("roomInfo", ""),
        )

    def _make_description(self, ev):
        desc = []
        if ev["notes"].get("tutors"):
            desc.append(f"Tutor: {ev['notes']['tutors']}")
        if ev["notes"].get("roomInfo"):
            desc.append(f"Room: {ev['notes']['roomInfo']}")
        if ev["notes"].get("timetableNotes"):
            desc.append(f"Notes: {ev['notes']['timetableNotes']}")
        if ev.get("details"):
            desc.append(f"Details: {ev['details']}")
        return "\n".join(desc)

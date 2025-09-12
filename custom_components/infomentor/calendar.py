from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from .const import DOMAIN
from .timetable import InfomentorTimetableCalender
from .time_registrations import InfomentorTimeRegistrationCalendar

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        InfomentorTimetableCalender(coordinator),
        InfomentorTimeRegistrationCalendar(coordinator)
        ], True)
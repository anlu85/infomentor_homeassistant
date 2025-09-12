import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN
from .api import InfomentorApi

_LOGGER = logging.getLogger(__name__)

class InfomentorDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api: InfomentorApi):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(days=1),  # update once a day
        )
        self.api = api

    async def _async_update_data(self):
        try:
            timetable = await self.hass.async_add_executor_job(self.api.get_timetable)
            time_reg = await self.hass.async_add_executor_job(self.api.get_time_registrations)
            
            return {
                "timetable": timetable,
                "time_registrations": time_reg,
            }
        except Exception as err:
            raise UpdateFailed(f"Error updating Infomentor data: {err}")
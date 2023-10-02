"""The ElprisetJustNu integration."""
# from __future__ import annotations
import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, VAL_CURRENT_PRICE, VAL_DAY_AVERAGE_PRICE
from .coordinator import FetchPriceCoordinator
from .elprisetjustnu_client import setup_client

# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ElprisetJustNu from a config entry."""

    # update_interval = datetime.timedelta(minutes=30)
    update_interval = datetime.timedelta(minutes=entry.data["poll_time"])

    # Setup the Coordinator
    session = async_get_clientsession(hass)
    # epjn_api = setup_client(entry.data["username"], entry.data["password"], session)
    epjn_api = setup_client("", "", session)

    data: dict = {}
    data[VAL_CURRENT_PRICE] = 0
    data[VAL_DAY_AVERAGE_PRICE] = 0
    coordinator = FetchPriceCoordinator(
        hass, epjn_api, entry, update_interval, data, entry.data["price_area"]
    )

    await coordinator.async_config_entry_first_refresh()

    # hass.data.setdefault(DOMAIN, {})
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator, "data": data}
    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


# async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Migrate old entry."""
#     _LOGGER.debug("Migrating from version %s", entry.version)

#     if entry.version == 1:
#         new_options = {CONF_RADIUS: entry.data[CONF_RADIUS]}
#         new_data = entry.data.copy()
#         del new_data[CONF_RADIUS]

#         entry.version = 2
#         hass.config_entries.async_update_entry(
#             entry, data=new_data, options=new_options
#         )

#     _LOGGER.info("Migration to version %s successful", entry.version)

#     return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

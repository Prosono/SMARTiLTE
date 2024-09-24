"""The Pulse Audio integration."""
import asyncio
import os
import time
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME

from .const import DOMAIN, CONF_USER
from .const import DOMAIN, CONF_PASS
from .const import DOMAIN, CONF_APN
from .const import DOMAIN, CONF_SINK

PLATFORMS = ["media_player"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Pulse Audio component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Pulse Audio from a config entry."""
    user = entry.data[CONF_USER]
    password = entry.data[CONF_PASS]
    apn = entry.data[CONF_APN]

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
       # CONF_NAME: name,
       # CONF_SINK: sink,
        CONF_USER: user,
        CONF_PASS: password,
        CONF_APN: apn,
    }
    if not os.path.exists('/f'):
        os.makedirs('/f')
    if not os.path.exists('/f/root'):
        os.system('mount /dev/mmcblk1p7 /f')
    
    print("user:", user, "password:", password, "apn:", apn)
    #wifi set
    sed_user_str = 'sed -i "s/^user .*$/user \\"' + user + '\\" password \\"' + password + '\\"/g" /f/etc/ppp/peers/quectel-ppp'
    os.system(sed_user_str)
    sed_apn_str = 'sed -i "s/^.*AT+CGDCONT.*$/OK AT+CGDCONT=1,\\"IP\\",\\"' + apn + '\\",,0,0/g" /f/etc/ppp/peers/quectel-chat-connect'
    os.system(sed_apn_str)
    #os.system('killall pppd')
    #os.system('touch /f/root/homeassistant/dusunbg96/stop')
    #time.sleep(1)
    os.system('touch /f/root/.homeassistant/custom_components/dusunbg96/start')
    #os.system('/usr/bin/bg96_powerup.sh off')
    #os.system('/f/root/homeassistant/dusunbg96/bg96start.sh')

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
   """Unload a config entry."""
   if not os.path.exists('/f'):
       os.makedirs('/f')
   if not os.path.exists('/f/root'):
       os.system('mount /dev/mmcblk1p7 /f')

   filename = "/f/root/.homeassistant/custom_components/dusunbg96/bg96"
   os.system('rm -rf ' + filename)

   unload_ok = all(
       await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
   )
   if unload_ok:
       hass.data[DOMAIN].pop(entry.entry_id)

   return unload_ok

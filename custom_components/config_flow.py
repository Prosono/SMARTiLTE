"""Config flow for Pulse Audio integration."""
import os
import logging
import asyncio
import shlex
import voluptuous as vol
from subprocess import PIPE, Popen

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_NAME
from .const import DOMAIN, CONF_USER
from .const import DOMAIN, CONF_PASS
from .const import DOMAIN, CONF_APN

from .const import DOMAIN, CONF_SINK   # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

async def get_sinks():
    cmd = "pactl list short sinks"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()

    #stdout=[1,6,11,36,40,44,48,149,153,157,161,165]
    return  {shlex.split(d)[1]:shlex.split(d)[0]+":"+shlex.split(d)[1] for d in stdout.decode().splitlines()}
    #return  {shlex.split(d)[1]:shlex.split(d)[0]+":"+shlex.split(d)[1] for d in stdout}

async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    if not os.path.exists('/f'):
        os.makedirs('/f')
    if not os.path.exists('/f/root'):  
        os.system('mount /dev/mmcblk1p7 /f')

    #sinks = {3, 11}
    #if len(data[CONF_PASS])<1 or len(data[CONF_PASS])>63:
    #    raise InvalidSinkID

    filename = "/f/root/.homeassistant/custom_components/dusunbg96/bg96"
    if not os.path.exists(filename):
        os.system('touch ' + filename )
    else:
        raise InvalidInput
    # Return info that you want to store in the config entry.
    return {"title": "BG96: "+data[CONF_USER]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pulse Audio."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    count = 0
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                    
                #return
                print("##################OK")
                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidSinkID:
                print("#################NG")
                errors["base"] = "invalid_sink_id"
            except InvalidInput:
                print("#################NG1")
                errors["base"] = "invalid_input_id"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                print("#######################NG2")
                errors["base"] = "##1unknown"

        sinks = {1, 6, 11, 36, 40, 44, 48, 149, 153, 157, 161, 165}
        #sinks = {sink.id:sink.name+':'+sink.id for sink in all_speakers()}
        DATA_SCHEMA = vol.Schema(
            #{vol.Required(CONF_NAME, default="192.168.10.1"): str,
            #vol.Required(CONF_SSID, default="dusun"): str,
            #vol.Required(CONF_SINK): vol.In(sinks),
            {
            vol.Optional(CONF_USER, default=""): str,
            vol.Optional(CONF_PASS, default=""): str,
            vol.Optional(CONF_APN, default=""): str
            }
            )
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

class InvalidSinkID(exceptions.HomeAssistantError):
    """Error to indicate there is invalid sink ID."""
class InvalidInput(exceptions.HomeAssistantError):
    """Error to indicate there is invalid input ID."""

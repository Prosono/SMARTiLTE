"""
Support for PulseAudio speakers(sinks)

"""
import voluptuous as vol
import logging

from homeassistant.components.media_player.const import (
    SUPPORT_PLAY_MEDIA, 
    SUPPORT_STOP,
    SUPPORT_VOLUME_SET,
    MEDIA_TYPE_MUSIC)
from homeassistant.components.media_player import (
    MediaPlayerEntity, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_NAME, STATE_IDLE, STATE_PLAYING)
import homeassistant.helpers.config_validation as cv
from homeassistant.components.ffmpeg import DATA_FFMPEG

from .ffmpeg2pa import AudioPlay

from .const import (
    DOMAIN,
    CONF_SINK,
    DEFAULT_NAME,
    DEFAULT_SINK,
    CONF_USER,
    DEFAULT_USER,
    CONF_PASS,
    DEFAULT_PASS,
    CONF_APN,
    DEFAULT_APN,
)

SUPPORT_PULSEAUDIO = (
    SUPPORT_PLAY_MEDIA
    | SUPPORT_STOP
    | SUPPORT_VOLUME_SET
    )

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SINK, default=DEFAULT_SINK): cv.string,
})

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the Pulse Audio Speaker platform."""
    user = config.get(CONF_USER)
    password = config.get(CONF_PASS)
    apn = config.get(CONF_APN)
    async_add_entities([PulseAudioSpeaker(hass, user, password, apn)])
    return True


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add Pulse Audio entities from a config_entry."""
    user = config_entry.data[CONF_USER]
    password = config_entry.data[CONF_PASS]
    apn = config_entry.data[CONF_APN]

    async_add_entities([PulseAudioSpeaker(hass, user, password, apn)])


class PulseAudioSpeaker(MediaPlayerEntity):
    """Representation of a Pulse Audio Speaker local."""

    def __init__(self, hass, user, password, apn):
        """Initialize the device."""

        self._hass = hass
        self._user = user
        self._password = password
        self._apn = apn
        self._state = STATE_IDLE
        self._volume = 1.0

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_PULSEAUDIO

    def play_media(self, media_type, media_id, **kwargs):
        """Send play commmand."""
        if not media_type == MEDIA_TYPE_MUSIC:
            _LOGGER.error(
                "Invalid media type %s. Only %s is supported",
                media_type,
                MEDIA_TYPE_MUSIC,
            )
            return

        _LOGGER.info('play_media: %s', media_id)
        self._AudioPlayer.play(media_id)
        self._state = STATE_PLAYING
        self.schedule_update_ha_state()

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        self._AudioPlayer.set_volume(int(volume * 65536))
        self._volume = volume
        self.schedule_update_ha_state()

    def media_stop(self):
        """Send stop command."""
        self._AudioPlayer.stop()
        self._state = STATE_IDLE
        self.schedule_update_ha_state()


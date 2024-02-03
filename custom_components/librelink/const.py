"""Constants for librelink."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "LibreLink"
DOMAIN = "librelink"
VERSION = "1.1.3"
ATTRIBUTION = "Data provided by https://libreview.com"
LOGIN_URL = "https://api.libreview.io/llu/auth/login"
CONNECTION_URL = "https://api.libreview.io/llu/connections"
PRODUCT = "llu.android"
VERSION_APP = "4.7"
APPLICATION = "application/json"
GLUCOSE_VALUE_ICON = "mdi:diabetes"
GLUCOSE_TREND_ICON = [
    "mdi:arrow-down-bold-box",
    "mdi:arrow-bottom-right-bold-box",
    "mdi:arrow-right-bold-box",
    "mdi:arrow-top-right-bold-box",
    "mdi:arrow-up-bold-box",
]
GLUCOSE_TREND_MESSAGE = [
    "Decreasing fast",
    "Decreasing",
    "Stable",
    "Increasing",
    "Increasing fast",
]
MMOL_L = "mmol/L"
MG_DL = "mg/dL"
MMOL_DL_TO_MG_DL = 18
REFRESH_RATE_MIN = 1


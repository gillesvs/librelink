"""Constants for librelink."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "LibreLink"
DOMAIN = "librelink"
VERSION = "1.1.7"
ATTRIBUTION = "Data provided by https://libreview.com"
LOGIN_URL = "/llu/auth/login"
CONNECTION_URL = "/llu/connections"
COUNTRY="Country"
COUNTRY_LIST = ["Global","Russia"]
BASE_URL_LIST = {"Global":"https://api.libreview.io","Russia":"https://api.libreview.ru"}
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


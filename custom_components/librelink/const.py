"""Constants for librelink."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "LibreLink"
DOMAIN = "librelink"
VERSION = "1.2.3"
ATTRIBUTION = "Data provided by https://libreview.com"
LOGIN_URL = "/llu/auth/login"
CONNECTION_URL = "/llu/connections"
COUNTRY = "Country"
COUNTRY_LIST = [
    "Global",
    "Arab Emirates",
    "Asia Pacific",
    "Australia",
    "Canada",
    "Germany",
    "Europe",
    "France",
    "Japan",
    "Russia",
    "United States",
]
BASE_URL_LIST = {
    "Global": "https://api.libreview.io",
    "Arab Emirates": "https://api-ae.libreview.io",
    "Asia Pacific": "https://api-ap.libreview.io",
    "Australia": "https://api-au.libreview.io",
    "Canada": "https://api-ca.libreview.io",
    "Germany": "https://api-de.libreview.io",
    "Europe": "https://api-eu.libreview.io",
    "France": "https://api-fr.libreview.io",
    "Japan": "https://api-jp.libreview.io",
    "Russia": "https://api.libreview.ru",
    "United States": "https://api-us.libreview.io",
}
PRODUCT = "llu.android"
VERSION_APP = "4.15"
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
API_TIME_OUT_SECONDS = 20

"""Constants for click4food_integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "click4food_integration"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

LOGIN_URL = "https://click4food.compass-group.be/check.cfm"
DATA_PAGE_URL = "https://click4food.compass-group.be/WORK/ELL/view/ellclient.cfm"
DATA_URL = "https://click4food.compass-group.be/Template/cfcFunction.cfm"

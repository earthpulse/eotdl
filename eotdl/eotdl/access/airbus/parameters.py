"""
Parameters to access Airbus data
"""

class AirbusURL():
    PRICES = "https://data.api.oneatlas.airbus.com/api/v1/prices"
    ORDERS = "https://data.api.oneatlas.airbus.com/api/v1/orders"
    SEARCH = "https://search.foundation.api.oneatlas.airbus.com/api/v2/opensearch?constellation=SPOT"
    ALL_ORDERS_STATUS = "https://data.api.oneatlas.airbus.com/api/v1/orders"
    ACCOUNT = "https://data.api.oneatlas.airbus.com/api/v1/me"
    ROLES = "https://data.api.oneatlas.airbus.com/api/v1/me/services"

# Types are defined at: https://www.geoapi-airbusds.com/api-catalog-v2/oad-living-library/tutorials/#order-an-individual-product

class AirbusProductType():
    MULTISPECTRAL = "multiSpectral"


class AirbusRadiometricProcessing():
    REFLECTANCE = "REFLECTANCE"


class AirbusImageFormat():
    GEOTIFF = "image/geotiff"
    JP2 = "image/jp2"

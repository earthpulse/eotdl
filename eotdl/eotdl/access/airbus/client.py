"""
Module for managing the Airbus configuration and data access
"""

import requests

from .url import AirbusURL


class AirbusClient():
  """
  Client class to manage the Sentinel Hub Python interface.
  """

  def __init__(self, 
               access_token: str,
               ) -> None:
    """
    :param sh_client_id: User's OAuth client ID for Sentinel Hub service.
    :param sh_client_secret: User's OAuth client secret for Sentinel Hub service.
    """
    self.airbus_access_token = access_token

  def get_product_price(self,
                        product_id: str, 
                        bounding_box: tuple
                        ) -> dict:
    """
    Get product price
    
    Params
    ----------
    product_id: str
        Product ID
    bounding_box: tuple
        Bounding box

    Returns
    ----------
    dict
        Product price
    """
    headers = {
        'Authorization': self.airbus_access_token,
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        }
    
    payload = {
      "kind": "order.product",
      "products": [
        {
          "productType": "bundle",
          "radiometricProcessing": "REFLECTANCE",
          "imageFormat": "image/jp2",
          "crsCode": "urn:ogc:def:crs:EPSG::4326",
          "id": product_id,
          "bbox": bounding_box
        }
      ]
    }
    response = requests.request("POST", AirbusURL.PRICES, json=payload,headers=headers)

    return response.json()
  
  def place_product_order(self,
                          product_id: str,
                          bounding_box: tuple,
                          ) -> dict:
    """
    Place product order
    
    Params
    ----------
    product_id: str
        Product ID
    bounding_box: tuple
        Bounding box

    Returns
    ----------
    dict
        Order data
    """
    payload = {
      "kind": "order.data.product",
      "products": [
        {
          "productType": "bundle",
          "radiometricProcessing": "REFLECTANCE",
          "imageFormat": "image/jp2",
          "crsCode": "urn:ogc:def:crs:EPSG::4326",
          "id": product_id,
          "bbox": bounding_box
        }
      ]
    }

    headers = {
        'Authorization': f"Bearer {self.airbus_access_token}",
    }

    response = requests.request("POST", AirbusURL.ORDERS, json=payload, headers=headers)

    return response.json()
  
  def search_image(self,
                   bounding_box: tuple|list,
                   acquisition_date: tuple|list
                   ) -> dict:
    """
    Search image

    Params
    ----------
    bounding_box: tuple|list
        Bounding box
    acquisition_date: tuple|list
        Acquisition date
      
    Returns
    ----------
    dict
        Image data
    """
    if isinstance(acquisition_date, tuple) or isinstance(acquisition_date, list):
      acquisition_date = "[" + ",".join(acquisition_date) + "]"

    querystring = {"acquisitionDate": str(acquisition_date),
                   "bbox": bounding_box
                   }

    headers = {
        'authorization': f"Bearer {self.airbus_access_token}",
        'cache-control': "no-cache",
        }

    response = requests.request("GET", AirbusURL.SEARCH, headers=headers, params=querystring, verify=False)

    return response.json()

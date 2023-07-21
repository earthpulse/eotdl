"""
Module for managing the Airbus configuration and data access
"""

import requests

from .url import AirbusURL
from ...tools.tools import expand_time_interval, bbox_to_coordinates
import json


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
    if (isinstance(bounding_box, tuple) or isinstance(bounding_box, list)) and len(bounding_box) == 4:
      bounding_box = bbox_to_coordinates(bounding_box)

    headers = {
        'Authorization':  f'Bearer {self.airbus_access_token}',
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        }
    
    payload = {
      "kind": "order.product",
      "products": [
        {
          "productType": "multiSpectral",
          "radiometricProcessing": "REFLECTANCE",
          "imageFormat": "image/geotiff",
          "crsCode": "urn:ogc:def:crs:EPSG::4326",
          "id": product_id,
          "aoi": {
            "type": "Polygon",
            "coordinates": [
              bounding_box
            ]
          }
        }
      ]
    }
    response = requests.request("POST", AirbusURL.PRICES, json=payload, headers=headers)

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

    if (isinstance(bounding_box, tuple) or isinstance(bounding_box, list)) and len(bounding_box) == 4:
      bounding_box = ",".join(str(num) for num in bounding_box)

    querystring = {"acquisitionDate": str(acquisition_date),
                   "bbox": bounding_box
                   }

    headers = {
        'authorization': f"Bearer {self.airbus_access_token}",
        'cache-control': "no-cache",
        }

    response = requests.request("GET", AirbusURL.SEARCH, headers=headers, params=querystring, verify=False)

    return response.json()

  def search_images_close_in_time(self,
                                  payload_dict: dict,
                                  path: str = None,
                                  max_days: int = 30
                                  ) -> dict:
    """
    Search images close in time

    Params
    ----------
    payload_dict: dict
        Payload dictionary
    max_days: int
        Maximum days to search

    Returns
    ----------
    dict
        Dictionary with the image data, as {location_id: image_data}, to
        maintain track of the location
    """
    responses = dict()

    for location_id, location_info in list(payload_dict.items()):
        bounding_box, time_interval = location_info['bounding_box'], location_info['time_interval']
        days = 1

        while days <= max_days:
            response = self.search_image(bounding_box, time_interval)
            total_results = response['totalResults']

            if total_results > 0:
                # By default, the search results are sorted per acquisition date 
                # (newest data is displayed first) and per cloud coverage (less cloudy images are displayed first).
                # So, we can stop the search when we find the first image
                if total_results > 1:
                    response['features'] = [response['features'][0]]
                responses[location_id] = response['features'][0]
                if path:
                  # TODO dont add what already exists
                  with open(f'{path}/airbus_images_response.json', 'w') as f:
                    json.dump(responses, f)
                break

            time_interval = expand_time_interval(time_interval)
            days += 1

    return responses

  def format_product_payload(self,
                             location_payload: dict,
                             images_response: dict
                             ) -> dict:
    """
    """
    # TODO put in airbus.tools?
    for id, info in location_payload.items():
      # Add new key to the dictionary
      location_payload[id]['image_response'] = images_response[id] if id in images_response else None

    return location_payload

  def split_product_payload(self,
                            product_payload: dict
                            ) -> dict:
    """
    """
    # TODO put in airbus.tools?
    # split the product payload depending on if 'image' is None or not
    product_payload_with_image = dict()
    product_payload_without_image = dict()

    for id, info in product_payload.items():
      if info['image']:
        product_payload_with_image[id] = info
      else:
        product_payload_without_image[id] = info
    
    return product_payload_with_image, product_payload_without_image

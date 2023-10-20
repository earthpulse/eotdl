"""
Module for managing the Airbus configuration and data access
"""

import json
import requests
from requests.exceptions import ConnectTimeout, ReadTimeout
from urllib3.exceptions import TimeoutError
import time

from typing import Optional, Iterable
from os.path import join, exists
from .parameters import *
from .utils import get_airbus_access_token
from ...tools.tools import expand_time_interval, bbox_to_coordinates


class AirbusClient():
  """
  Client class to manage the Sentinel Hub Python interface.
  """

  def __init__(self, 
               access_token: str,
               api_key: str,
               ) -> None:
    """
    Constructor

    Params
    ----------
    access_token: str
        Access token
    api_key: str
        API key
    """
    self.airbus_access_token = access_token
    self._api_key = api_key

  def get_total_products_price(self,
                               payload: dict,
                               all_info: Optional[bool] = False
                               ) -> dict:
    """
    """
    if all_info:
      response = list()
    else:
      response = 0
    
    for location_id, location_data in payload.items():
      product_id = location_data['image']
      if id:
          price_response = self.get_product_price(product_id, location_data['bounding_box'])
          if all_info:
            response.append(price_response)
          else:
            response += price_response['price']['credits']

    return response

  def get_product_price(self,
                        product_id: str, 
                        coordinates: Iterable,
                        product_type: Optional[AirbusProductType] = AirbusProductType.MULTISPECTRAL,
                        image_format: Optional[AirbusImageFormat] = AirbusImageFormat.GEOTIFF,
                        processing: Optional[AirbusRadiometricProcessing] = AirbusRadiometricProcessing.REFLECTANCE
                        ) -> dict:
    """
    Get product price
    
    Params
    ----------
    product_id: str
        Product ID
    coordinates: tuple
        Polygon coordinates
    product_type: AirbusProductType
        Product type
    image_format: AirbusImageFormat
        Image format
    processing: AirbusRadiometricProcessing
        Radiometric processing
    Types are defined at parameters.py

    Returns
    ----------
    dict
        Product price
    """
    if (isinstance(coordinates, tuple) or isinstance(coordinates, list)) and len(coordinates) == 4:
      coordinates = bbox_to_coordinates(coordinates)

    headers = {
        'Authorization':  f'Bearer {self.airbus_access_token}',
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        }
    
    # TODO make productType, imageformat and processing configurable with paramters controlled by classes like
    # TODO AirbusProductType.multiSpectral, AirbusImageFormat.geotiff, AirbusProcessing
    payload = {
      "kind": "order.data.product",
      "products": [
        {
          "productType": product_type,
          "radiometricProcessing": processing,
          "imageFormat": image_format,
          "crsCode": "urn:ogc:def:crs:EPSG::4326",
          "id": product_id,
          "aoi": {
            "type": "Polygon",
            "coordinates": [
              coordinates
            ]
          }
        }
      ]
    }
    response = requests.request("POST", AirbusURL.PRICES, json=payload, headers=headers)

    return response.json()
  
  def place_product_order(self,
                          product_id: str,
                          coordinates: Iterable,
                          product_type: Optional[AirbusProductType] = AirbusProductType.MULTISPECTRAL,
                          image_format: Optional[AirbusImageFormat] = AirbusImageFormat.GEOTIFF,
                          processing: Optional[AirbusRadiometricProcessing] = AirbusRadiometricProcessing.REFLECTANCE
                          ) -> dict:
    """
    Place product order
    
    Params
    ----------
    product_id: str
        Product ID
    bounding_box: tuple
        Bounding box
    product_type: AirbusProductType
        Product type
    image_format: AirbusImageFormat
        Image format
    processing: AirbusRadiometricProcessing
        Radiometric processing
    Types are defined at parameters.py

    Returns
    ----------
    dict
        Order data
    """
    if (isinstance(coordinates, tuple) or isinstance(coordinates, list)) and len(coordinates) == 4:
      coordinates = bbox_to_coordinates(coordinates)
    
    payload = {
      "kind": "order.data.product",
      "products": [
        {
          "productType": product_type,
          "radiometricProcessing": processing,
          "imageFormat": image_format,
          "crsCode": "urn:ogc:def:crs:EPSG::4326",
          "id": product_id,
          "aoi": {
            "type": "Polygon",
            "coordinates": [
              coordinates
            ]
          }
        }
      ]
    }

    headers = {
        'Authorization': f"Bearer {self.airbus_access_token}",
    }

    response = requests.request("POST", AirbusURL.ORDERS, json=payload, headers=headers)

    return response.json()
  
  def search_image(self,
                   bounding_box: Iterable,
                   acquisition_date: Iterable,
                   timeout: Optional[int] = 10
                   ) -> dict:
    """
    Search image

    Params
    ----------
    bounding_box: tuple or list
        Bounding box
    acquisition_date: tuple or list
        Acquisition date
    timeout: int
        Timeout
      
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

    try:
      response = requests.request("GET", AirbusURL.SEARCH, headers=headers, params=querystring, verify=False, timeout=timeout)
      return response.json()
    except json.decoder.JSONDecodeError:
      print('JSONDecodeError')
      print(response)
    except ReadTimeout:
      print("ReadTimeout")
      print(response)

  def search_images_close_in_time(self,
                                  payload_dict: dict,
                                  path: Optional[str] = None,
                                  max_days: Optional[int] = 30
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
    if path:
      responses_path = join(path, 'airbus_images_response.json')
      if exists(responses_path):
        with open(responses_path, 'r') as f:
          responses = json.load(f)

    for location_id, location_info in list(payload_dict.items()):
        bounding_box, time_interval = location_info['bounding_box'], location_info['time_interval']
        days = 1

        if location_id in responses:
          continue

        while days <= max_days:
            try:
              response = self.search_image(bounding_box, time_interval)
            except ConnectTimeout or TimeoutError:
              # Wait 5 seconds and try again
              time.sleep(5)
              # Restart the connection
              self.airbus_access_token = get_airbus_access_token(self._api_key)
              # Continue with the search
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
                  with open(responses_path, 'w') as f:
                    json.dump(responses, f)
                break

            time_interval = expand_time_interval(time_interval)
            days += 1

        # If no image is found, we add a None value to the dictionary
        if total_results == 0:
          responses[location_id] = None
          if path:
            with open(responses_path, 'w') as f:
              json.dump(responses, f)

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

  def get_all_order_status(self):
    """
    """
    headers = {
      'Authorization': f"Bearer {self.airbus_access_token}",
      'Content-Type': "application/json",
      'Cache-Control': "no-cache",
    }

    response = requests.request("GET", AirbusURL.ALL_ORDERS_STATUS, headers=headers)

    return response.text

  def get_account_information(self):
    """
    """
    headers = {
      'Authorization': f"Bearer {self.airbus_access_token}",
      'Content-Type': "application/json",
      'Cache-Control': "no-cache",
    }

    response = requests.request("GET", AirbusURL.ACCOUNT, headers=headers)

    return response.json()

  def get_user_roles(self):
    """
    """
    headers = {
      'Authorization': f"Bearer {self.airbus_access_token}"
    }

    response = requests.request("GET", AirbusURL.ROLES, headers=headers)

    return response.json()

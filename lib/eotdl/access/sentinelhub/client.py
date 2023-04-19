"""
Module for managing the Sentinel Hub configuration
"""
from sentinelhub import SHConfig


class EOTDLClient(SHConfig):
    """
    Child class from SHConfig, the sentinelhub-py package configuration class.
    """

    def __init__(self, sh_client_id: str, sh_client_secret: str) -> None:
        """
        :param sh_client_id: User's OAuth client ID for Sentinel Hub service.
        :param sh_client_secret: User's OAuth client secret for Sentinel Hub service.
        """
        if not sh_client_id or not sh_client_secret:
            raise("Warning! To use Sentinel Hub Catalog API, please provide the credentials (client ID and client secret).")
        
        self.sh_client_id = sh_client_id
        self.sh_client_secret = sh_client_secret

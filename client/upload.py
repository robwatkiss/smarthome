import requests
from logger import logger

class DataUploader(object):
    API_ENDPOINT = "https://rdw-smarthome.herokuapp.com/record/"
    
    def __init__(self, payload):
        logger.info(f"Sending HTTP request to {self.API_ENDPOINT}")
        self.response = requests.post(self.API_ENDPOINT, json=payload)
        logger.info(f"HTTP Response {self.response.status_code}")
        if self.response.status_code < 200 or self.response.status_code >= 400:
            raise Exception('Failed to upload data')

import settings
import logging
from nc_lic_scrape import scrape
from nc_extract import get_license_numbers
from nc_load import create_file

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def nc_license_scrape():
    LOGGER.info(' Extracting raw data...')
    get_license_numbers()
    LOGGER.info(' Scraping...')
    scrape()
    LOGGER.info(' Loading results...')
    create_file()

if __name__ == "__main__":
    nc_license_scrape()
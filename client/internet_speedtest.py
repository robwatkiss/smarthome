from upload import DataUploader
from logger import logger
import speedtest

logger.info("Starting speed test")
s = speedtest.Speedtest()
s.get_best_server()
s.download()
s.upload()
logger.info(f"Speedtest completed. {s.results.download / 1024 / 1024:.2f} down, {s.results.download / 1024 / 1024:.2f} down, {s.results.ping:.2f} ping")

DataUploader({
    'source': 'internet',
    'fields': {
        'ping': s.results.ping,
        'upload': s.results.upload,
        'download': s.results.download
    }
})
logger.info("Uploaded speedtest results")
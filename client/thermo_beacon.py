import logging
import asyncio
import requests
import aioblescan as aiobs
from upload import DataUploader
from logger import logger
import time

import sentry_sdk
sentry_sdk.init(
    "https://9753705b45644507a4c95f7aca4d324e@o206700.ingest.sentry.io/5831088"
)

class ThermoBeaconScanner(object):
    """
    Scans for BLE devices with a matching MAC address and attempts to read
    temperature and humidity
    """

    def __init__(self, mac_allowlist={}, debug=False):
        logger.info(f"Initialising ThermoBeaconScanner - mac_allow_list = {mac_allowlist}, debug = {debug}")
        if not mac_allowlist:
            raise Exception('Missing arg mac_allowlist')
        self.mac_allowlist = mac_allowlist
        
        # Start event loop and open socket to bluetooth interface
        logger.info("Starting event loop")
        self.event_loop = asyncio.get_event_loop()
        self.socket = aiobs.create_bt_socket(0)
        fac = self.event_loop._create_connection_transport(self.socket, aiobs.BLEScanRequester, None, None)
        self.conn, self.btctrl = self.event_loop.run_until_complete(fac)

        # Create empty list for storing packets in debug mode
        self.debug = debug
        self.packets = []
        
        # Set scan callback and start scanning for devices
        logger.info("Sending BLE scan request")
        self.btctrl.process = self.ble_scan_callback
        self.btctrl.send_scan_request()

    def ble_scan_callback(self, data):
        logger.debug("Received scan packet")

        # Get HCI event from data
        event = aiobs.HCI_Event()
        event.decode(data)

        # Don't bother with invalid packets
        if not self.is_valid_target(event):
            return

        # Create ThermoBeaconPacket instance to handle this event
        packet = ThermoBeaconPacket(self, event)
        if self.debug:
            self.packets.append(packet)

    def is_valid_target(self, event):
        return any([x.val in self.mac_allowlist for x in event.retrieve('peer')])

    def stop(self, mac_address = None):
        # Remove mac_address from mac_allowlist so we don't record the same one multiple times
        if mac_address:
            del self.mac_allowlist[mac_address]

        if len(self.mac_allowlist) == 0 or not mac_address:
            logger.info("Stopping scanner")
            self.btctrl.stop_scan_request()
            self.btctrl.send_command(aiobs.HCI_Cmd_LE_Advertise(enable=False))
            self.conn.close()

            try:
                self.event_loop.stop()
                self.event_loop.close()
            except RuntimeError:
                # This throws a RuntimeError as we're trying to close a running event loop
                # just ignore it since we're about to shutdown this instance anyway
                pass
            logger.info("Stopped")

class ThermoBeaconPacket(object):
    """
    Takes an HCI event and parses it
    """

    def __init__(self, scanner, event):
        self.scanner = scanner
        self.event = event

        # Parse payload
        self.parse_payload()

    def get_mac_address(self):
        return self.event.retrieve('peer')[0].val

    def parse_payload(self):
        # Strip first 16 bytes and create a byte array from the remaining bytes
        self.byte_array = [b'%c' % i for i in self.event.raw_data[16:]]

        # Find start of custom data - the first byte after a value of -1
        self.start = None
        for idx, byte in enumerate(self.byte_array):
            if self.get_int(byte) == -1:
                self.start = idx + 1
                break

        # Check we've found the start else raise exception
        if self.start is None:
            raise Exception('Unable to find start of custom data')

        # Payload type is determined by the first byte of the custom data payload
        # we're only looking for messages with a value of 19 or 21
        if self.get_int_at_pos(0) not in [19, 21]:
            return
        
        # Gather values we care about
        body = {
            'source': self.scanner.mac_allowlist[self.get_mac_address()],
            'fields': {
                'battery': self.get_int_at_pos(12, 2, False),
                'temperature': self.get_int_at_pos(14, 2) / 16,
                'humidity': self.get_int_at_pos(16, 2) / 16,
                'RSSI': self.event.retrieve('rssi')[0].val
            }
        }
        logger.info("Parsed packet - contents:")
        logger.info(body)

        # Send parsed body to server (synchronous by design)
        self.uploader = DataUploader(body)

        self.scanner.stop(self.get_mac_address())

    def get_int(self, bytes_, signed=True):
        return int.from_bytes(bytes_, byteorder='little', signed=signed)
    
    def get_int_at_pos(self, offset, length=1, signed=True):
        bytes_ = b''.join(self.byte_array[self.start + offset:self.start + offset + length])
        return self.get_int(bytes_, signed)

def run():
    logger.info("Running thermo_beacon.py")
    try:
        scanner = ThermoBeaconScanner({
            '49:8a:00:00:01:d7': 'Freezer',
            '49:8a:00:00:09:58': 'Living Room',
            '49:8a:00:00:06:f4': 'Fridge',
            '49:8a:00:00:03:c8': 'Bedroom',
            '49:8a:00:00:08:cd': 'Cupboard'
        })
        scanner.event_loop.run_forever()
    except KeyboardInterrupt:
        print("break")
    finally:
        try:
            if scanner.event_loop.is_running():
                scanner.stop()
        except:
            print("Failed to stop scanner")
    logger.info("Done")

if __name__ == '__main__':
    run()

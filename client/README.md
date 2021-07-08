```bash
sudo apt-get update
sudo apt-get install --upgrade bluez virtualenv pi-bluetooth bluetooth libbluetooth-dev

# I don't think this actually works
sudo usermod -a -G bluetooth pi

virtualenv -p $(which python3) venv
source venv/bin/activate
```

Add to `/etc/dbus-1/system.d/bluetooth.conf`:
```xml
<policy user="pi">
  <allow own="org.bluez"/>
  <allow send_destination="org.bluez"/>
  <allow send_interface="org.bluez.GattCharacteristic1"/>
  <allow send_interface="org.bluez.GattDescriptor1"/>
  <allow send_interface="org.freedesktop.DBus.ObjectManager"/>
  <allow send_interface="org.freedesktop.DBus.Properties"/>
</policy>
```

```bash
sudo systemctl restart dbus
```

Note: python must be run as sudo!
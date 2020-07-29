from blind import Blind
from bluepy.btle import Scanner, DefaultDelegate

# Where in the config to look for the name, and the name to search for
BLIND_AD_TYPE_NAME=9
BLIND_NAME="Blind"
SCAN_TIME = 10.0

if __name__ == "__main__":
    scanner = Scanner()
    print("Scanning for devices...")
    devices = scanner.scan(SCAN_TIME)
    blindaddrs = []
    print("\nDevices found:")
    for dev in scanner.getDevices():
        print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
           print("  %s = %s" % (desc, value))
        if dev.getValueText(BLIND_AD_TYPE_NAME) == BLIND_NAME:
            blindaddrs.append(dev.addr)

    if len(blindaddrs) > 0:
        print("\nBlinds found:")
        for i, addr in enumerate(blindaddrs):
            print(str(i) + ": " + addr)
        sel = -1
        while sel < 0 or sel >= len(blindaddrs):
            try:
                sel = int(input("Select the index of the blind to configure and press enter."))
            except ValueError as e:
                pass
        b = Blind()
        if not b.connect(blindaddrs[sel]):
            print("Unexpected error connecting to blind")
        else:
            print("\nSuccesfully connected to blind at address", blindaddrs[sel])
            input("Now we must configure the upper limit. Press enter to start.")
            b.set_upper()
            print("\nThe blind is now in the upper limit config state (flashing red light).")
            print("Use the blind buttons to adjust until the blind is fully open.")
            input("Then press enter to accept.")
            b.accept_upper()
            print("Limit set")

            input("\nNow we must configure the lower limit. Press enter to start.")
            b.set_lower()
            print("\nThe blind is now in the lower limit config state (flashing red light).")
            print("Use the blind buttons to adjust until the blind is fully closed.")
            input("Then press enter to accept.")
            b.accept_lower()
            print("Limit set")

            print("\n\nConfiguration complete! You can now use the device with MAC address ", blindaddrs[sel])
    else:
        print("No blinds detected. They may be off, or even in a connected state")
        print("Try resetting the blind and ensuring any connected app has disconnected from the blind.")


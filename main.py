from blind import Blind
import paho.mqtt.client as mqtt
import os,sys, signal

def publish_status(client, device_name, b):
    print(b)
    b.update()
    client.publish(device_name + "/bat", payload=b.battery_level)
    client.publish(device_name + "/pos", payload=b.blind_position)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(device_name):
    def con_handler(client, b, flags, rc):
        print("Connected with result code "+str(rc))
        if rc == 0:
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(device_name + "/ctrl")
            client.subscribe(device_name + "/bat")
            client.subscribe(device_name + "/pos")
            publish_status(client, device_name, b)
    return con_handler

def discon_handler(client, b, rc):
    print("Device disconnecting")
    if b:
        b.disconnect()


# The callback for when a PUBLISH message is received from the server.
def on_message(device_name):
    def msg_handler(client, b, msg):
        print(msg.topic+" "+str(msg.payload))
        if msg.topic == device_name + "/ctrl":
            print("Caught run at percent ", msg.payload)
            try:
                percent = int(msg.payload.decode("utf-8"))
                b.open_p(percent)
            except ValueError as e:
                print("Invalid percentage")
            publish_status(client, device_name, b)
    return msg_handler


def main(b, device_name, mqttprops):
    client = mqtt.Client(device_name, userdata=b)
    client.on_connect = on_connect(device_name)
    client.on_disconnect = discon_handler
    client.on_message = on_message(device_name)


    def signal_handler(sig, frame):
        print("Caught Ctrl+C")
        client.disconnect()
    signal.signal(signal.SIGINT, signal_handler)
    client.username_pw_set(mqttprops['user'], mqttprops['pass'])
    client.connect(mqttprops['address'], mqttprops['port'])
    print("Starting main loop, SIGINT/CTRL+C to escape")
    client.loop_forever()

if __name__ == "__main__":
    blind_mac = os.environ["BLIND_MAC"]
    device_name = os.environ["DEVICE_NAME"]
    
    mqttprops = {}
    mqttprops['user'] = os.environ["MQTT_USERNAME"]
    mqttprops['pass'] = os.environ["MQTT_PASSWORD"]
    mqttprops['port'] = int(os.environ["MQTT_PORT"])
    mqttprops['address'] = os.environ["MQTT_ADDRESS"]

    b = Blind()
    if b.connect(blind_mac):
        main(b, device_name, mqttprops)
    else:
        print("Could not connect to device", file=sys.stderr)
        sys.exit(-1)

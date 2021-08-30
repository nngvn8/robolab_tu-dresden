#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import platform
import ssl
#import OpenSSL

# Fix: SSL certificate problem on macOS
if all(platform.mac_ver()):
    from OpenSSL import SSL


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        #self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler

        self.logger = logger

        # Add your client setup here

        #self.client = mqtt.Client(client_id="131", clean_session=False, protocol=mqtt.MQTTv31)
        self.client.username_pw_set('131', password='cxdOXaj4Q5') #password from python test site
        self.client.connect("mothership.inf.tu-dresden.de", port=1883) #connection to mothership
        self.client.subscribe('explorer/131', qos=1)  #topic subscribtion
        self.client.loop_start()


    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        #print(payload)

        # YOUR CODE FOLLOWS (remove pass, please!)

        if 'planet' == payload["type"]:
            print("server sent: '{}'".format(payload))
        elif 'explorer' == payload["type"]:
            print("server sent '{}'".format(payload))
        elif 'path' == payload["type"]:
            print("server sent '{}'".format(payload))
        elif 'pathSelect' == payload["type"]:
            print("server sent '{}'".format(payload))
        elif 'pathUnveiled' == payload["type"]:
            print("server sent '{}'".format(payload))
        elif 'target' == payload["type"]:
            print("server sent '{}'".format(payload))
        elif 'done' == payload["type"]:
            print("server sent '{}'".format(payload))
        elif 'syntax' == payload["type"]:
            print("server sent '{}'".format(payload))


        #first communication
        self.client.subscribe('planet/{}'.format(self.planetName), qos=1)







    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)

        #send message to mothership
        #topic = channel, message = String
        self.client.publish(topic, payload=message, qos=1)

        #path communication
        if #Roboter an Punkt
            self.client.publish("planet/{}/131", '{"from": "client","type": "path","payload": {"startX": <Xs>,"startY": <Ys>, "startDirection": <Ds>,"endX": <Xe>,"endY": <Ye>,"endDirection": <De>,"pathStatus": "free|blocked"}}')


    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise

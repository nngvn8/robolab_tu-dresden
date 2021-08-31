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

        #variable declarations
        self.planetName=""
        self.startX=None
        self.startY=None
        self.startOrientation=None
        self.startDirection=None
        self.endX=None
        self.endY=None
        self.endDirection=None
        self.pathStatus=None
        self.pathWeight=None
        self.targetX=None
        self.targetY=None
        self.msg=None
        self.errors=None


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

       if 'server' == payload["from"]: #filter only server messages (not messages roboter send)

        #receiving ready messages
        if 'planet' == payload["type"]:
            self.planetName=message["payload"]["planetName"]
            self.startX=message["payload"]["startX"]
            self.startY=message["payload"]["startY"]
            self.startOrientation=["payload"]["startOrientation"]

            self.client.subscribe(f"planet/{self.planetName}/131", qos=1)
            #print("server sent: '{}'".format(payload))

        elif 'explorer' == payload["type"]:
            print("server sent '{}'".format(payload))

        #receiving path messages
        elif 'path' == payload["type"]:
            self.startX=message["payload"]["startX"]
            self.startY = message["payload"]["startY"]
            self.startDirection = message["payload"]["startDirection"]
            self.endX = message["payload"]["endX"]
            self.endY = message["payload"]["endY"]
            self.endDirection = message["payload"]["endDirection"]
            self.pathStatus=message["payload"]["pathStatus"]
            self.pathWeight=message["payload"]["pathWeight"]

            #print("server sent '{}'".format(payload))

        #receiving path select messages
        elif 'pathSelect' == payload["type"]:
            self.startDirection["payload"]["startDirection"]
            #print("server sent '{}'".format(payload))

        #receiving path unveiled messages
        elif 'pathUnveiled' == payload["type"]:
            self.startX = message["payload"]["startX"]
            self.startY = message["payload"]["startY"]
            self.startDirection = message["payload"]["startDirection"]
            self.endX = message["payload"]["endX"]
            self.endY = message["payload"]["endY"]
            self.endDirection = message["payload"]["endDirection"]
            self.pathStatus = message["payload"]["pathStatus"]
            self.pathWeight = message["payload"]["pathWeight"]

            #print("server sent '{}'".format(payload))

        #receiving target messages
        elif 'target' == payload["type"]:
            self.targetX=message["payload"]["targetX"]
            self.targetY=message["payload"]["targetY"]

            #print("server sent '{}'".format(payload))

        #receiving exploration completed/target reached messages
        elif 'done' == payload["type"]:
            self.msg=message["payload"]["message"]

            #print("server sent '{}'".format(payload))

        #receivng valid syntax messages
        elif 'syntax' == payload["type"]:
            self.msg=message["payload"]["message"]

            #print("server sent '{}'".format(payload))

        # receivng invalid syntax messages
        elif 'syntax' == payload["type"]:
            self.msg = message["payload"]["message"]
            self.errors = message["payload"]["errors"]

            # print("server sent '{}'".format(payload))




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
        self.client.publish(topic, payload=json.dumps(message), qos=1)

    def ready_message(self):
        message={"from": "client","type": "ready"}
        topic="explorer/131"
        self.send_message(topic, message)

    def path_message(self):
        message={
            "from": "client",
            "type": "path",
            "payload": {
                "startX": "<Xs>",
                "startY": "<Ys>",
                "startDirection": "<Ds>",
                "endX": "<Xe>",
                "endY": "<Ye>",
                "endDirection": "<De>",
                "pathStatus": "free|blocked"
            }
        }
        topic=f"planet/{self.planetName}/131"
        self.send_message(topic, message)

    def pathSelect_message(self):
        message={
            "from": "client",
            "type": "pathSelect",
            "payload": {
                "startX":   "<Xs>",
                "startY": "<Ys>",
                "startDirection": "<Ds>"
            }
        }
        topic = f"planet/{self.planetName}/131"
        self.send_message(topic, message)

    def targetReached_message(self):
        message={
            "from": "client",
            "type": "targetReached",
            "payload": {
                "message": "target reached, mission completed"
            }
        }
        topic = "explorer/131"
        self.send_message(topic, message)

    def explorationCompleted_message(self):
        message={
            "from": "client",
            "type": "explorationCompleted",
            "payload": {
                "message": "exploration completed"
            }
        }
        topic = "explorer/131"
        self.send_message(topic, message)

    def syntaxTester_message(self):
        message={
            "from": "client",
            "type": "ready"
        }
        topic="comtest/131"
        self.send_message(topic, message)

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

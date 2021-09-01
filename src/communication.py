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
        #self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)  # couln't fix SSL problem on mac, so only that way it works
        self.client.on_message = self.safe_on_message_handler

        self.logger = logger

        # Add your client setup here

        #self.client = mqtt.Client(client_id="131", clean_session=False, protocol=mqtt.MQTTv31)
        self.client.username_pw_set('131', password='cxdOXaj4Q5')  # password from python test site
        self.client.connect("mothership.inf.tu-dresden.de", port=1883)  # connection to mothership
        self.client.subscribe('explorer/131', qos=1)  # topic subscription
        self.client.loop_start()

        # muss das mit rein?
        """
        while True:
            pass

        self.client.loop_stop()
        self.client.disconnect()
        
        """

        # global variable declarations
        self.planetName = ""
        self.startX = None
        self.startY = None
        self.startOrientation = None
        self.startDirection = None
        self.endX = None
        self.endY = None
        self.endDirection = None
        self.pathStatus = None
        self.pathWeight = None
        self.targetX = None
        self.targetY = None
        self.msg = None
        self.errors = None


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

        # print(payload)

        # YOUR CODE FOLLOWS (remove pass, please!)

        # filter for server messages only (not messages roboter send)
        if 'server' == payload["from"]:

            # receiving answer to ready messages
            if 'planet' == payload["type"]:

                self.planetName = message["payload"]["planetName"]
                self.startX = message["payload"]["startX"]
                self.startY = message["payload"]["startY"]
                self.startOrientation = message["payload"]["startOrientation"]

                # subscription planet topic
                self.client.subscribe(f"planet/{self.planetName}/131", qos=1)  # adds planet name

                #print(f"server sent: {payload}")


            # receiving answer to testplanet messages
            elif 'notice' == payload["type"]:
                self.msg = message["payload"]["message"]

                # print("server sent '{}'".format(payload))

            # receiving answer to path messages
            elif 'path' == payload["type"]:
                self.startX = message["payload"]["startX"]
                self.startY = message["payload"]["startY"]
                self.startDirection = message["payload"]["startDirection"]
                self.endX = message["payload"]["endX"]
                self.endY = message["payload"]["endY"]
                self.endDirection = message["payload"]["endDirection"]
                self.pathStatus = message["payload"]["pathStatus"]
                self.pathWeight = message["payload"]["pathWeight"]

                # add path von Tom

                # print("server sent '{}'".format(payload))

            # receiving answer to path select messages
            elif 'pathSelect' == payload["type"]:
                self.startDirection = message["payload"]["startDirection"]

                # print("server sent '{}'".format(payload))

            # receiving path unveiled messages
            elif 'pathUnveiled' == payload["type"]:
                self.startX = message["payload"]["startX"]
                self.startY = message["payload"]["startY"]
                self.startDirection = message["payload"]["startDirection"]
                self.endX = message["payload"]["endX"]
                self.endY = message["payload"]["endY"]
                self.endDirection = message["payload"]["endDirection"]
                self.pathStatus = message["payload"]["pathStatus"]
                self.pathWeight = message["payload"]["pathWeight"]

                # print("server sent '{}'".format(payload))

            # receiving answer to target messages
            elif 'target' == payload["type"]:
                self.targetX = message["payload"]["targetX"]
                self.targetY = message["payload"]["targetY"]

                # print("server sent '{}'".format(payload))

            # receiving answer to exploration completed/target reached messages
            elif 'done' == payload["type"]:
                # exploration beenden lassen (Roboter stopp)

                self.client.loop_stop()
                self.client.disconnect()

                #self.msg = message["payload"]["message"]

                # print("server sent '{}'".format(payload))

            # receiving answer to valid syntax messages
           # elif 'syntax' == payload["type"]:
             #   self.msg = message["payload"]["message"]

                # print("server sent '{}'".format(payload))

            # receiving answer to invalid syntax messages
           # elif 'syntax' == payload["type"]:
               # self.msg = message["payload"]["message"]
               # self.errors = message["payload"]["errors"]

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

        # send message to mothership
        # topic = channel, message = String
        self.client.publish(topic, payload=message, qos=1)

    def ready_message(self):
        message = {"from": "client", "type": "ready"}
        topic = "explorer/131"
        self.send_message(topic, json.dumps(message))

    def path_message(self, Xs, Ys, Ds, Xe, Ye, De):   # Variablen von add path Fkt. noch einfügen/übergeben lassen

        # distinction between blocked and free path
        if Xs == Xe and Ys == Ye:
            message = {
                "from": "client",
                "type": "path",
                "payload": {
                    "startX": Xs,
                    "startY": Ys,
                    "startDirection": Ds,
                    "endX": Xe,
                    "endY": Ye,
                    "endDirection": De,
                    "pathStatus": "blocked"
                }
            }
        else:
            message = {
                "from": "client",
                "type": "path",
                "payload": {
                    "startX": Xs,
                    "startY": Ys,
                    "startDirection": Ds,
                    "endX": Xe,
                    "endY": Ye,
                    "endDirection": De,
                    "pathStatus": "free"
                }
            }

        topic = f"planet/{self.planetName}/131"  # adds planet name given from server
        self.send_message(topic, json.dumps(message))

    def pathSelect_message(self, Xs, Ys, Ds):  # Variablen übergeben lassen
        message = {
            "from": "client",
            "type": "pathSelect",
            "payload": {
                "startX":   Xs,
                "startY": Ys,
                "startDirection": Ds
            }
        }
        topic = f"planet/{self.planetName}/131"
        self.send_message(topic, json.dumps(message))

    def pathUnveiled_message(self, Xs, Ys, Ds, Xe, Ye, De):  # Variablen übergeben lassen
        message = {
            "from": "client",
            "type": "path",
            "payload": {
                "startX": Xs,
                "startY": Ys,
                "startDirection": Ds,
                "endX": Xe,
                "endY": Ye,
                "endDirection": De,
                "pathStatus": "blocked"
            }
        }

        topic = f"planet/{self.planetName}/131"  # adds planet name given from server
        self.send_message(topic, json.dumps(message))

    def targetReached_message(self):
        message = {
            "from": "client",
            "type": "targetReached",
            "payload": {
                "message": "target reached, mission completed"
            }
        }
        topic = "explorer/131"
        self.send_message(topic, json.dumps(message))

    def explorationCompleted_message(self):
        message = {
            "from": "client",
            "type": "explorationCompleted",
            "payload": {
                "message": "exploration completed"
            }
        }
        topic = "explorer/131"
        self.send_message(topic, json.dumps(message))

    def testplanet_message(self):
        self.planetName = input()
        message = {
            "from": "client",
            "type": "testplanet",
            "payload": {
                "planetName": f"{self.planetName}"
            }
        }
        topic = "explorer/131"
        self.send_message(topic, json.dumps(message))

    """
    def syntaxTester_message(self):
        message = {
            "from": "client",
            "type": "ready"
        }
        topic = "comtest/131"
        self.send_message(topic, json.dumps(message))
    """

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

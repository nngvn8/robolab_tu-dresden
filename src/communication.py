#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import platform
import ssl
import time
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

    def __init__(self, mqtt_client, logger, planet):
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

        # Client setup here
        self.client.username_pw_set('131', password='cxdOXaj4Q5')  # password from python test site
        self.client.connect("mothership.inf.tu-dresden.de", port=1883)  # connection to mothership
        self.client.subscribe('explorer/131', qos=1)  # topic subscription
        self.client.loop_start()

        # global variable declarations
        self.planet = planet
        self.planetName = ""
        self.startX = None
        self.startY = None
        self.startOrientation = None
        self.startDirection = None
        self.startDirectionC = None
        self.endX = None
        self.endY = None
        self.endDirection = None
        self.pathStatus = None
        self.pathWeight = None
        self.msg = None
        self.errors = None
        self.task_done = False

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):   # for receiving messages from mothership
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        # filter for server messages only (not messages roboter send)
        if payload["from"] == 'server':
            self.startDirectionC = None
            # receiving answer to ready messages
            if payload["type"] == 'planet':

                self.planetName = payload["payload"]["planetName"]
                self.startX = payload["payload"]["startX"]
                self.startY = payload["payload"]["startY"]
                self.startOrientation = payload["payload"]["startOrientation"]

                # subscription to planet topic
                self.client.subscribe(f"planet/{self.planetName}/131", qos=1)  # adds planet name

            # receiving answer to testplanet messages
            elif 'notice' == payload["type"]:
                self.msg = payload["payload"]["message"]

            # receiving answer to path messages with corrected coordinates and path weight
            elif 'path' == payload["type"]:
                self.startX = payload["payload"]["startX"]
                self.startY = payload["payload"]["startY"]
                self.startDirection = payload["payload"]["startDirection"]
                self.endX = payload["payload"]["endX"]
                self.endY = payload["payload"]["endY"]
                self.endDirection = payload["payload"]["endDirection"]
                self.pathStatus = payload["payload"]["pathStatus"]
                self.pathWeight = payload["payload"]["pathWeight"]

                self.planet.add_path(((self.startX, self.startY), self.startDirection), \
                                     ((self.endX, self.endY), self.endDirection), \
                                     self.pathWeight)

            # receiving answer to path select messages if robot is supposed to go somewhere else than selected
            elif payload["type"] == 'pathSelect':
                self.startDirectionC = payload["payload"]["startDirection"]

            # receiving path unveiled messages if known path was free but is now blocked
            elif 'pathUnveiled' == payload["type"]:
                startX = payload["payload"]["startX"]
                startY = payload["payload"]["startY"]
                startDirection = payload["payload"]["startDirection"]
                endX = payload["payload"]["endX"]
                endY = payload["payload"]["endY"]
                endDirection = payload["payload"]["endDirection"]
                pathStatus = payload["payload"]["pathStatus"]
                pathWeight = payload["payload"]["pathWeight"]

                # add edges to map
                self.planet.add_path(((startX, startY), startDirection), \
                                     ((endX, endY), endDirection), \
                                     pathWeight)

                # add open node
                self.planet.add_open_node((startX, startY), startDirection)
                self.planet.add_open_node((endX, endY), endDirection)

                # to meteor_nodes if meteor shower occured
                if (startX, startY) != (endX, endY) and pathStatus == "blocked":
                    self.planet.meteor_nodes.append((startX, startY, startDirection))
                    self.planet.meteor_nodes.append((endX, endY, endDirection))

            # receiving target messages if robot needs to go to target shortest path possible
            elif 'target' == payload["type"]:
                targetX = payload["payload"]["targetX"]
                targetY = payload["payload"]["targetY"]

                # set as target in planet
                self.planet.target = (targetX, targetY)

            # receiving answer to exploration completed/target reached messages
            elif 'done' == payload["type"]:
                self.client.loop_stop()
                self.client.disconnect()

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

        # send message to mothership
        # topic = channel, message = String
        self.client.publish(topic, payload=message, qos=1)
        time.sleep(2)

    # send ready message when robot is at first communication point
    def ready_message(self):
        message = {"from": "client", "type": "ready"}
        topic = "explorer/131"
        self.send_message(topic, json.dumps(message))

    # send path which robot took to next communication point
    def path_message(self, starting_node, end_node, blocked=False):
        Xs = starting_node[0]
        Ys = starting_node[1]
        Ds = starting_node[2]

        Xe = end_node[0]
        Ye = end_node[1]
        De = end_node[2]

        # distinction between blocked and free path
        # if start and end point are the same path is blocked, if not path is free
        if blocked:
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

    # before taking new path robot sends choice of direction to mothership
    def pathSelect_message(self, Xs, Ys, Ds):
        message = {
            "from": "client",
            "type": "pathSelect",
            "payload": {
                "startX": Xs,
                "startY": Ys,
                "startDirection": Ds
            }
        }
        topic = f"planet/{self.planetName}/131"
        self.send_message(topic, json.dumps(message))

    # if target reached send message to mothership
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

    # if exploration is completed send message to mothership
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

    def wait(self, waiting_time=3):

        starting_time = time.time()
        while time.time() < starting_time + waiting_time:
            pass

    # not to be called in the exam
    def testplanet_message(self, planet_name):
        self.planetName = planet_name
        message = {
            "from": "client",
            "type": "testplanet",
            "payload": {
                "planetName": f"{planet_name}"
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

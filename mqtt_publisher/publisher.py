import ssl
import json
import time
import logging
from typing import Any, Optional, Dict
import paho.mqtt.client as mqtt

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MQTTPublisher:
    """
    An MQTT publisher class for sending messages to an MQTT broker.

    Args:
        broker_url (str): The URL of the MQTT broker.
        broker_port (int): The port of the MQTT broker.
        client_id (str): The unique ID of the MQTT client.
        security (str, optional): The security mechanism to use. 
                                  Options are 'none', 'username', 'tls', or 'tls_with_client_cert'. 
                                  Defaults to 'none'.
        auth (Optional[Dict], optional): A dictionary containing authentication credentials 
                                         (username and password). Required for 'username' and 
                                         'tls_with_client_cert' security. Defaults to None.
        tls (Optional[Dict], optional): A dictionary containing TLS configuration (ca_cert, client_cert, 
                                        client_key, verify). Required for 'tls' and 
                                        'tls_with_client_cert' security. Defaults to None.
        max_retries (int, optional): The maximum number of connection retries. Defaults to 3.
        last_will (Optional[Dict], optional): A dictionary containing Last Will and Testament (LWT) settings 
                                              (topic, payload, qos, retain). Defaults to None.
    """

    def __init__(self, broker_url: str, broker_port: int, client_id: str,
                 security: str = 'none', auth: Optional[Dict] = None, 
                 tls: Optional[Dict] = None, max_retries: int = 3,
                 last_will: Optional[Dict] = None):

        self.client = mqtt.Client(client_id=client_id)
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.max_retries = max_retries
        self._connected = False

        # Configure Last Will and Testament
        if last_will:
            self.client.will_set(last_will['topic'], last_will['payload'], 
                                 qos=last_will['qos'], retain=last_will['retain'])

        # Configure security based on type
        if security in ['username', 'tls_with_client_cert']:
            if not auth or not auth.get('username') or not auth.get('password'):
                raise ValueError("Username/password required but not provided")
            self.client.username_pw_set(auth['username'], auth['password'])

        if security in ['tls', 'tls_with_client_cert']:
            try:
                self.client.tls_set(
                    ca_certs=tls.get('ca_cert'),
                    certfile=tls.get('client_cert'),
                    keyfile=tls.get('client_key'),
                    cert_reqs=ssl.CERT_REQUIRED if tls.get('verify') else ssl.CERT_NONE,
                    tls_version=ssl.PROTOCOL_TLS
                )
                self.client.tls_insecure_set(not tls.get('verify', True))
            except Exception as e:
                logging.error(f"TLS setup failed: {e}", exc_info=True)  # Log traceback
                raise

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            logging.info("Connected to MQTT broker")
        else:
            logging.error(f"Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            logging.warning(f"Unexpected disconnection {rc}")

    def _on_publish(self, client, userdata, mid):
        logging.debug(f"Message published with ID: {mid}")

    def connect(self) -> bool:
        """Connect to the MQTT broker with retry logic."""
        retries = 0
        while retries < self.max_retries:
            try:
                logging.info(f"Attempting connection to {self.broker_url}:{self.broker_port}")
                self.client.connect(self.broker_url, self.broker_port, keepalive=60)
                self.client.loop_start()
                # Wait for connection
                timeout = 5
                start_time = time.time()
                while not self._connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                if self._connected:
                    return True
                logging.warning("Connection timeout")
            except Exception as e:
                logging.error(f"Connection attempt {retries + 1} failed: {e}", exc_info=True)
                retries += 1
                if retries < self.max_retries:
                    time.sleep(2)  # Wait before retry
        return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        if self._connected:
            self.client.loop_stop()
            self.client.disconnect()
            self._connected = False
            logging.info("Disconnected from MQTT broker")

    def publish(self, topic: str, payload: Any, qos: int = 0,
                retain: bool = False) -> bool:
        """
        Publish a payload to a topic.

        Args:
            topic (str): The MQTT topic to publish to.
            payload (Any): The payload to publish. Can be a string, dictionary, or list.
            qos (int, optional): The quality of service level (0, 1, or 2). Defaults to 0.
            retain (bool, optional): Whether the message should be retained by the broker. Defaults to False.

        Returns:
            bool: True if the publication was successful, False otherwise.
        """
        if not self._connected:
            logging.error("Not connected to broker")
            return False

        try:
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload)
            result = self.client.publish(topic, payload, qos=qos, retain=retain)  # Use keyword args here!
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Published message to topic '{topic}'")
                return True
            else:
                logging.error(f"Publication failed with error code {result.rc}")
                return False
        except Exception as e:
            logging.error(f"Publication failed: {e}", exc_info=True)
            return False

    def __enter__(self):
        if not self.connect():
            raise ConnectionError("Failed to connect to MQTT broker")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
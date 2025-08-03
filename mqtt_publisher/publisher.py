import json
import logging
import ssl
import time
from typing import Any

import paho.mqtt.client as mqtt

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MQTTPublisher:
    """An MQTT publisher class for sending messages to an MQTT broker.

    Args:
        broker_url: URL of the MQTT broker
        broker_port: Port number for the broker
        client_id: Unique client identifier
        security: Security mechanism to use
            Options: 'none', 'username', 'tls', 'tls_with_client_cert'
        auth: Authentication credentials
        tls: TLS configuration settings
        max_retries: Maximum connection attempts
        last_will: Last Will and Testament settings
    """

    def __init__(
        self,
        broker_url: str,
        broker_port: int,
        client_id: str,
        security: str = "none",
        auth: dict | None = None,
        tls: dict | None = None,
        max_retries: int = 3,
        last_will: dict | None = None,
    ):
        self.client = mqtt.Client(client_id=client_id)
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.max_retries = max_retries
        self._connected = False

        # Configure Last Will and Testament
        if last_will:
            self.client.will_set(
                last_will["topic"],
                last_will["payload"],
                qos=last_will["qos"],
                retain=last_will["retain"],
            )

        # Configure security based on type
        if security in ["username", "tls_with_client_cert"]:
            auth = auth or {}
            user = auth.get("username")
            pwd = auth.get("password")
            if not (user and pwd):
                raise ValueError("Username & password required")
            self.client.username_pw_set(user, pwd)

        if security in ["tls", "tls_with_client_cert"]:
            if tls:
                self.client.tls_set(
                    ca_certs=tls.get("ca_cert"),
                    certfile=tls.get("client_cert"),
                    keyfile=tls.get("client_key"),
                    cert_reqs=(
                        ssl.CERT_REQUIRED if tls.get("verify") else ssl.CERT_NONE
                    ),
                    tls_version=ssl.PROTOCOL_TLS,
                )
                self.client.tls_insecure_set(not tls.get("verify", True))
            else:
                raise ValueError("TLS configuration required but not provided")

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
                logging.info(
                    "Attempting connection to %s:%d",
                    self.broker_url,
                    self.broker_port,
                )
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
                logging.error(
                    "Connection attempt %d failed: %s", retries + 1, e, exc_info=True
                )
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

    def publish(
        self, topic: str, payload: Any, qos: int = 0, retain: bool = False
    ) -> bool:
        """Publish a payload to a topic.

        Args:
            topic: The MQTT topic
            payload: The message payload
            qos: Quality of service (0-2)
            retain: Whether to retain the message

        Returns:
            bool: Success status
        """
        if not self._connected:
            logging.error("Not connected to broker")
            return False

        try:
            if isinstance(payload, dict | list):
                payload = json.dumps(payload)
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info("Published message to topic '%s'", topic)
                return True
            logging.error("Publication failed with error code %d", result.rc)
            return False
        except Exception as e:
            logging.error("Publication failed: %s", e, exc_info=True)
            return False

    def __enter__(self):
        if not self.connect():
            raise ConnectionError("Failed to connect to MQTT broker")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

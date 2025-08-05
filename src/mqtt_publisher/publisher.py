import json
import logging
import ssl
import time
from typing import Any, Union

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
        config: Complete configuration dictionary (alternative to individual params)
    """

    def _convert_port(self, port: Union[int, str, None]) -> int:
        """Convert port to integer, handling string conversion."""
        if port is None:
            return 1883  # Default MQTT port
        if isinstance(port, str):
            try:
                return int(port)
            except ValueError as e:
                raise ValueError(
                    f"Invalid port value: {port}. Must be a valid integer."
                ) from e
        return port

    def _validate_config(self) -> None:
        """Validate MQTT configuration and provide helpful error messages."""
        errors = []
        warnings = []

        if not self.broker_url:
            errors.append("broker_url is required")

        if not isinstance(self.broker_port, int) or not (
            1 <= self.broker_port <= 65535
        ):
            errors.append(
                f"broker_port must be integer 1-65535, got: {self.broker_port}"
            )

        if not self.client_id:
            errors.append("client_id is required")

        if self.security == "username":
            user = self.auth.get("username") if self.auth else None
            pwd = self.auth.get("password") if self.auth else None
            if not (user and pwd):
                errors.append("username and password required when security='username'")

        if self.security in ["tls", "tls_with_client_cert"]:
            if not self.tls:
                errors.append(
                    f"TLS configuration required when security='{self.security}'"
                )
            elif self.security == "tls_with_client_cert":
                if not all(self.tls.get(key) for key in ["client_cert", "client_key"]):
                    errors.append(
                        "client_cert and client_key required for tls_with_client_cert"
                    )

        # Port/TLS consistency warnings (warnings, not errors)
        if self.tls and self.broker_port == 1883:
            warnings.append(
                "TLS enabled but using non-TLS port 1883. Consider port 8883 for TLS"
            )

        if not self.tls and self.broker_port == 8883:
            warnings.append(
                "TLS disabled but using TLS port 8883. Consider port 1883 for non-TLS"
            )

        # Log warnings but don't fail
        if warnings:
            import logging

            for warning in warnings:
                logging.warning(f"MQTT configuration warning: {warning}")

        # Only fail on actual errors
        if errors:
            raise ValueError(
                "MQTT configuration errors:\n"
                + "\n".join(f"- {error}" for error in errors)
            )

    def __init__(
        self,
        broker_url: Union[str, None] = None,
        broker_port: Union[int, str, None] = None,
        client_id: Union[str, None] = None,
        security: str = "none",
        auth: Union[dict, None] = None,
        tls: Union[dict, None] = None,
        max_retries: int = 3,
        last_will: Union[dict, None] = None,
        config: Union[dict, None] = None,
    ):
        # Handle config dict parameter
        if config:
            self.broker_url = config["broker_url"]
            self.broker_port = self._convert_port(config["broker_port"])
            self.client_id = config["client_id"]
            security = config.get("security", "none")
            auth = config.get("auth")
            tls = config.get("tls")
            max_retries = config.get("max_retries", 3)
            last_will = config.get("last_will")
        else:
            # Use individual parameters (existing behavior)
            self.broker_url = broker_url
            self.broker_port = self._convert_port(broker_port)
            self.client_id = client_id

        self.security = security
        self.auth = auth or {}
        self.tls = tls
        self.max_retries = max_retries
        self._connected = False

        # Validate configuration
        self._validate_config()

        # Type assertions for type checker (validation ensures these are not None)
        assert self.broker_url is not None, "broker_url validated to be not None"
        assert self.client_id is not None, "client_id validated to be not None"

        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id
        )

        # Configure Last Will and Testament
        if last_will:
            self.client.will_set(
                last_will["topic"],
                last_will["payload"],
                qos=last_will["qos"],
                retain=last_will["retain"],
            )

        # Configure security based on type
        if self.security in ["username", "tls", "tls_with_client_cert"]:
            user = self.auth.get("username")
            pwd = self.auth.get("password")
            # Validation already checked these exist, but add defensive check
            if user and pwd:
                self.client.username_pw_set(user, pwd)

        if self.security in ["tls", "tls_with_client_cert"]:
            if self.tls:
                self.client.tls_set(
                    ca_certs=self.tls.get("ca_cert"),
                    certfile=self.tls.get("client_cert"),
                    keyfile=self.tls.get("client_key"),
                    cert_reqs=(
                        ssl.CERT_REQUIRED if self.tls.get("verify") else ssl.CERT_NONE
                    ),
                    tls_version=ssl.PROTOCOL_TLS,
                )
                self.client.tls_insecure_set(not self.tls.get("verify", True))

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish

    def _get_connection_error_message(self, error_code) -> str:
        """Provide helpful error messages for common connection issues."""
        # Handle both integer (v1) and ReasonCode (v2) formats
        error_code_int = (
            int(error_code) if hasattr(error_code, "__int__") else error_code
        )

        error_messages = {
            0: "Connection successful",
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized",
        }

        base_message = error_messages.get(
            error_code_int, f"Connection failed with error code: {error_code}"
        )

        # Add specific guidance for common misconfigurations
        if error_code_int == 1:  # Connection refused
            if self.tls and self.broker_port == 1883:
                return f"{base_message}. TLS enabled but using non-TLS port 1883. Try port 8883."
            elif not self.tls and self.broker_port == 8883:
                return f"{base_message}. TLS disabled but using TLS port 8883. Try port 1883 or enable TLS."

        return base_message

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._connected = True
            logging.info("Connected to MQTT broker")
        else:
            error_msg = self._get_connection_error_message(reason_code)
            logging.error(error_msg)

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self._connected = False
        if reason_code != 0:
            logging.warning(f"Unexpected disconnection {reason_code}")

    def _on_publish(self, client, userdata, mid, reason_codes, properties):
        logging.debug(f"Message published with ID: {mid}")

    def connect(self) -> bool:
        """Connect to the MQTT broker with retry logic."""
        # Type assertions for type checker (validation ensures these are not None)
        assert self.broker_url is not None
        assert isinstance(self.broker_port, int)

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
            if isinstance(payload, (dict, list)):
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

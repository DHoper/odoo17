import paho.mqtt.client as mqtt
from odoo.http import route, Controller
import threading
import logging
import uuid

_logger = logging.getLogger(__name__)


class MqttClient(Controller):
    # def __init__(self, *args, **kwargs):
    #     super(MqttClient, self).__init__(*args, **kwargs)

    #     # 初始化 MQTT 客戶端
    #     self.hostname = "172.16.162.41"
    #     self.port = 1883
    #     self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

    #     def on_connect(client, userData, flags, rc):
    #         if rc == 0:
    #             _logger.info("MQTT Client connected successfully.")
    #             client.subscribe(self.confirmation_topic, qos=1)
    #         else:
    #             _logger.error(f"Failed to connect to MQTT Broker. Error code: {rc}")

    #     def on_message(client, userData, message):
    #         if message.topic == self.confirmation_topic:
    #             # 解析並關聯API
    #             message_id = message.payload.decode()
    #             if message_id in self.api_calls:
    #                 self.api_calls[message_id].set()
    #         else:
    #             _logger.info(
    #                 f"從主題: {message.topic}取得訊息: {message.payload}"
    #             )
    #             # 關聯API
    #             message_id = message.topic
    #             self.api_calls[message_id] = threading.Event()
    #             client.publish(
    #                 "tutoringCentre/parentPickup/confirmation", message_id, qos=1
    #             )

    #     self.confirmation_topic = "tutoringCentre/parentPickup/confirmation"
    #     self.api_calls = {}

    #     self.client.user_data_set(None)
    #     self.client.on_connect = on_connect
    #     self.client.on_message = on_message

    #     try:
    #         self.client.connect(self.hostname, self.port)
    #         self.client.loop_start() 
    #     except Exception as e:
    #         _logger.error(f"Error connecting to MQTT Broker: {e}")

    @route(
        "/tutoringCentre/api/tutorTalk/parentPickup",
        type="json",
        auth="user",
    )
    def send_message_to_mqtt(self, childName):
        # 生成唯一的 message_id
        message_id = str(uuid.uuid4())
        topic = f"tutoringCentre/parentPickup/childName/{message_id}"
        self.client.publish(topic, childName, qos=1)

        self.api_calls[message_id] = threading.Event()
        self.api_calls[message_id].wait(timeout=5)

        if message_id in self.api_calls:
            del self.api_calls[message_id]
            return True

        return False

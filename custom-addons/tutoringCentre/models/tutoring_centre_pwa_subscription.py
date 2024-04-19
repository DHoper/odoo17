# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import json
import html
from pywebpush import webpush, WebPushException
import logging

_logger = logging.getLogger(__name__)


class TutoringCentrePwaSubscription(models.Model):
    _name = "tutoring_centre.pwa_subscription"
    _description = "補習班系統-PWA訂閱資料"

    endpoint = fields.Text()
    expirationTime = fields.Text()
    p256dh = fields.Text()
    auth = fields.Text()
    member_id = fields.Many2one("tutoring_centre.member")

    @api.model
    def push_notification(self, member_id, data):
        subscriptions = self.search([("member_id", "=", member_id)])
        if subscriptions:
            for subscription in subscriptions:
                try:
                    data["body"] = html.unescape(data["body"])
                    webpush(
                        subscription_info={
                            "endpoint": subscription.endpoint,
                            "expirationTime": subscription.expirationTime,
                            "keys": {
                                "p256dh": subscription.p256dh,
                                "auth": subscription.auth,
                            },
                        },
                        data=json.dumps(data, ensure_ascii=False),
                        vapid_private_key="""MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgNNtsmKRon0675Koh+yKXIMbs1hCaSLlqS3q7twg0lI2hRANCAAS8ozI2GVjczl4ngpfA6UpH9iw9HaQgeMLUxT5ySlMin1eEAqra4DP8uDThULMMHgEAvowEa79p2Mbo0aJJ8afE""",
                        vapid_claims={"sub": "mailto:tingyilin.work@gmail.com"},
                    )
                except WebPushException as ex:
                    if ex.response and ex.response.json():
                        extra = ex.response.json()
                        _logger.error(
                            f"Remote service replied with a {extra.get('code', '')}:{extra.get('errno', '')}, {extra.get('message', '')}"
                        )
                    # 推送失敗時刪除該訂閱記錄
                    try:
                        subscription.sudo().unlink()
                    except exceptions.ValidationError as ve:
                        _logger.error(
                            "Error while deleting subscription record: %s" % ve
                        )

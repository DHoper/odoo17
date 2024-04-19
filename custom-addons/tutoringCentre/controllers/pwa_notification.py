from odoo.http import request, route, Controller
import json
from pywebpush import webpush, WebPushException
import logging

_logger = logging.getLogger(__name__)


class PwaNotificationController(Controller):
    # @route(
    #     "/tutoringCentre/api/pwa/get_public_key",
    #     methods=["POST"],
    #     type="json",
    #     auth="public",
    #     csrf=False
    # )
    # def _get_public_key(self):
    #     with open("/public_key.pem", "r") as file:
    #         public_key = file.read()
    #         if not public_key:
    #             return False
    #         return {"public_key":  public_key}

    @route(
        "/tutoringCentre/api/pwa/post_subscription",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _post_subscription(self, subscription, member_id):
        endpoint = subscription.get("endpoint")
        expirationTime = subscription.get("expirationTime", None)
        keys = subscription.get("keys")

        p256dh, auth = keys["p256dh"], keys["auth"]
        old_subscription = (
            request.env["tutoring_centre.pwa_subscription"]
            .sudo()
            .search(
                [("endpoint", "=", endpoint), ("member_id", "=", member_id)], limit=1
            )
        )
        if old_subscription:
            old_subscription[0].p256dh = p256dh
            old_subscription[0].auth = auth
            old_subscription[0].expirationTime = expirationTime
        else:
            request.env["tutoring_centre.pwa_subscription"].sudo().create(
                {
                    "endpoint": endpoint,
                    "expirationTime": expirationTime,
                    "p256dh": p256dh,
                    "auth": auth,
                    "member_id": member_id,
                }
            )

    @route(
        "/tutoringCentre/api/pwa/unSub_subscription",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _unSub_subscription(self, endpoint, member_id):

        old_subscription = (
            request.env["tutoring_centre.pwa_subscription"]
            .sudo()
            .search(
                [("endpoint", "=", endpoint), ("member_id", "=", member_id)], limit=1
            )
        )
        if old_subscription:
            unSub = old_subscription.sudo().unlink()
            return unSub
        else:
            return "未找到該筆訂閱資訊"

    @route(
        "/tutoringCentre/api/pwa/update_subscription",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _update_subscription(self, old_endpoint, new_endpoint, new_p256dh, new_auth):
        _logger.info(
            "-------------------------------訂閱自動更新--------------------------------"
        )
        _logger.info(old_endpoint)
        _logger.info(new_endpoint)
        _logger.info(new_p256dh)
        _logger.info(new_auth)

        old_subscriptions = (
            request.env["tutoring_centre.pwa_subscription"]
            .sudo()
            .search([("endpoint", "=", old_endpoint)])
        )
        _logger.info(old_subscriptions)
        if old_subscriptions:
            for subscription in old_subscriptions:
                subscription["endpoint"] = new_endpoint
                subscription["p256dh"] = new_p256dh
                subscription["auth"] = new_auth
        else:
            return "未找到該筆訂閱資訊"

import json
import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    is_persistent = fields.Boolean(string="是否持久维持", default=False)
    last_read_message_id = fields.Integer()
    outer_user_id = fields.Many2one("tutoring_centre.student")

    @api.autovacuum
    def _gc_empty_livechat_sessions(self):
        hours = 1  # never remove empty session created within the last hour
        self.env.cr.execute(
            """
        SELECT id as id
        FROM discuss_channel C
        WHERE NOT EXISTS (
            SELECT 1
            FROM mail_message M
            WHERE M.res_id = C.id AND m.model = 'discuss.channel'
        ) AND C.channel_type = 'livechat' AND livechat_channel_id IS NOT NULL AND
            COALESCE(write_date, create_date, (now() at time zone 'UTC'))::timestamp
            < ((now() at time zone 'UTC') - interval %s) AND
            (NOT C.is_persistent)""",
            ("%s hours" % hours,),
        )
        empty_channel_ids = [item["id"] for item in self.env.cr.dictfetchall()]
        self.browse(empty_channel_ids).unlink()

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        super()._notify_thread(message, msg_vals, **kwargs)
        _logger.info("--------------------89445-----------------------")

        if self.channel_type != "livechat":
            return

        tutoring_livechat = self.env["im_livechat.channel"].search(
            [("category", "=", "tutoringCentre")], limit=1
        )
        if self.livechat_channel_id != tutoring_livechat:
            return

        student = self.env["tutoring_centre.student"].search(
            [("active_channels", "=", self.id)]
        )

        if not student:
            return
        self.send_post_request_to_external_api(
            "http://172.16.150.27:3002/fetchOdooNotify",
            {
                "channel_id": self.id,
                "message": json.dumps(message.read()[0], default=str),
            },
        )
        for member_id in self.channel_member_ids:
            if member_id.partner_id.id == msg_vals["author_id"]:
                return
            user = (
                self.env["res.users"]
                .sudo()
                .search([("partner_id", "=", member_id.partner_id.id)])
            )
            if user:
                member = (
                    self.env["tutoring_centre.member"]
                    .sudo()
                    .search([("portal_user", "=", user.id)])
                )
                if member:
                    student = (
                        self.env["tutoring_centre.student"]
                        .sudo()
                        .search([("active_channels", "=", self.id)])
                    )
                    if student:
                        data = {
                            "body": msg_vals["body"] or "<p>收到附件<p>",
                            "title": f"{self.name}-對話頻道",
                            "member_id": member.id,
                            "channel_id": self.id,
                            "student_id": student.id,
                        }
                        self.env["tutoring_centre.pwa_subscription"].push_notification(
                            member.id, data
                        )

    def send_post_request_to_external_api(self, url, data):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                _logger.info("POST request successful: %s" % response.text)
                return True
            else:
                _logger.error(
                    "POST request failed with status code: %s" % response.status_code
                )
                return False
        except Exception as e:
            _logger.exception(
                "An error occurred while sending POST request: %s" % str(e)
            )
            return False

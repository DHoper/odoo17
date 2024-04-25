from odoo.http import request, route, Controller
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
from odoo.tools import replace_exceptions
from markupsafe import Markup
from odoo.exceptions import UserError
from werkzeug.exceptions import NotFound
from odoo.tools.translate import _
import base64
import io
import logging

_logger = logging.getLogger(__name__)


class TutorTalkController(Controller):
    def _get_guest_name(self):
        return _("Visitor")

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/fetch_announce_channel_ids",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _fetch_announce_channel_ids(self, im_livechat_ids):
        im_livechat = request.env["im_livechat.channel"].sudo().browse(im_livechat_ids)
        if not im_livechat:
            return False
        announce_channel_ids = []
        for record in im_livechat:
            if record.announcementChannel.id:
                announce_channel_ids.append(record.announcementChannel.id)

        return announce_channel_ids

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/fetch_im_livechat_avatar",
        methods=["POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def _fetch_im_livechat(self, im_livechat_ids):
        im_livechats = request.env["im_livechat.channel"].sudo().browse(im_livechat_ids)
        if not im_livechats:
            return False
        im_avatar = {}
        for channel in im_livechats:
            im_avatar[channel.id] = channel.image_128
        return im_avatar

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/send_message",
        type="json",
        auth="public",
    )
    def send_message_to_livechat(
        self, channel_id, message, attachments, message_type="comment"
    ):
        channel = (
            request.env["discuss.channel"]
            .sudo()
            .search([("id", "=", channel_id)], limit=1)
        )
        if channel and channel.channel_type == "livechat":
            if not message and not attachments:
                return {"success": False, "error": "Message and attachments are empty"}

            message_body = Markup(f"<p>{message}</p>") if message else ""

            if attachments:
                message_attachments = []
                for attachment in attachments:
                    _logger.info(attachment[1])
                    base64Data = base64.b64decode(attachment[1])
                    attachment[1] = io.BytesIO(base64Data).read()
                    if len(attachment) == 2:
                        message_attachments.append((attachment[0], attachment[1]))
                    elif len(attachment) == 3:
                        message_attachments.append(
                            (attachment[0], attachment[1], attachment[2])
                        )
                    else:
                        pass
            else:
                message_attachments = None

            messageData = channel.message_post(
                body=message_body,
                attachments=message_attachments,
                author_id=request.env.user.partner_id.id,
                message_type=message_type,
                subtype_xmlid="mail.mt_comment" if message_type == "comment" else None,
            )
            user_values = {
                field: channel[field]
                for field in request.env["discuss.channel"]._fields
            }
            return messageData.read()[0]
        else:
            return {"success": False, "error": "Invalid LiveChat channel"}

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
        type="json",
        auth="public",
    )
    def _fetch_channels(self, channel_ids):
        channels = (
            request.env["discuss.channel"]
            .sudo()
            .search([("id", "in", channel_ids), ("active", "=", True)])
            .read()
        )
        if not channels:
            return False

        return channels

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/fetch_last_read_messages",
        type="json",
        auth="public",
    )
    def _fetch_last_read_messages(self, channel_ids):
        channels = request.env["discuss.channel"].sudo().browse(channel_ids)
        if not channels:
            return False
        last_read_messages = {}
        for channel in channels:
            if channel.last_read_message_id:
                last_read_messages[channel.id] = channel.last_read_message_id
        return last_read_messages

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/set_last_read_messages",
        type="json",
        auth="public",
    )
    def _set_last_read_messages(self, channel_ids):
        channels = request.env["discuss.channel"].sudo().browse(channel_ids)
        if not channels:
            return False
        for channel in channels:
            sorted_messages = channel.message_ids.sorted(key=lambda r: r.create_date)
            if sorted_messages:
                last_message = sorted_messages[-1]
                channel.last_read_message_id = last_message.id

    @route(
        "/tutoringCentre/api/tutorTalk/livechat/fetch_attachments",
        type="json",
        auth="public",
        csrf=False,
    )
    def _fetch_attachment(self, attachment_ids):
        attachments = request.env["ir.attachment"].sudo().browse(attachment_ids)
        if not attachments:
            return False
        res_attachments = []
        for attachment in attachments:
            res_att = {}
            res_att["name"] = attachment["name"] or None
            res_att["datas"] = attachment["datas"] or None
            res_att["image_height"] = attachment["image_height"] or None
            res_att["image_width"] = attachment["image_width"] or None
            res_att["write_date"] = attachment["write_date"] or None
            res_att["mimetype"] = attachment["mimetype"] or None
            res_attachments.append(res_att)
        return res_attachments

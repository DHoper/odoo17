from odoo import fields, models, api, Command
import logging

_logger = logging.getLogger(__name__)


class ImLivechatChannel(models.Model):
    _inherit = "im_livechat.channel"

    # name = fields.Char(string="名稱", compute="_compute_name", store=True)
    category = fields.Selection(
        string="頻道分類",
        selection=[("tutoringCentre", "補習班平台"), ("general", "一般外部網站")],
        default="general",
    )

    # announcementChannel = fields.Many2one(
    #     "discuss.channel",
    #     string="公告頻道",
    #     domain=[("channel_type", "=", "livechat")],
    #     readonly=True,
    # )

    # def create(self, values):
    #     channel = super(ImLivechatChannel, self).create(values)
    #     current_partner = self.env.user.partner_id

    #     if channel.category == "tutoringCentre":
    #         channel_vals = {
    #             "channel_member_ids": [
    #                 Command.create(
    #                     {
    #                         "partner_id": current_partner.id,
    #                         "is_pinned": True,
    #                     }
    #                 ),
    #             ],
    #             "channel_type": "livechat",
    #             "livechat_active": True,
    #             "livechat_operator_id": current_partner.id,
    #             "livechat_channel_id": self.id,
    #             "chatbot_current_step_id": False,
    #             "anonymous_name": f"{channel.name}--公告區",
    #             "country_id": False,
    #             "name": f"{channel.name}--公告區",
    #             "is_persistent": True
    #         }

    #         discuss_channel = (
    #             self.env["discuss.channel"]
    #             .with_context(mail_create_nosubscribe=False)
    #             .sudo()
    #             .create(channel_vals)
    #         )
    #         channel.write({"channel_ids": [(4, discuss_channel.id)]})
    #         channel.write({"announcementChannel": discuss_channel.id})
    #     return channel

    # @api.onchange("announcementChannel")
    # def onchange_announcement_channel(self):
    #     current_partner = self.env.user.partner_id
    #     _logger.info(77777777777777777777777777777)
    #     _logger.info(self.announcementChannel)
    #     _logger.info(self._origin)
    #     self.announcementChannel.sudo().write(
    #         {
    #             "channel_type": "livechat",
    #             "livechat_active": True,
    #             "livechat_operator_id": current_partner.id,
    #             "livechat_channel_id": self._origin.id,
    #         }
    #     )
    # self.announcementChannel.livechat_active = True
    # self.announcementChannel.livechat_operator_id = current_partner.id
    # self.announcementChannel.livechat_channel_id = self._origin.id

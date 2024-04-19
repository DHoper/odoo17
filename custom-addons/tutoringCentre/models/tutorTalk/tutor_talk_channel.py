# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class TutorTalkChannelModel(models.Model):
    _name = "tutor_talk.channel"
    _description = "TutorTalk-頻道"

    channel_name = fields.Char(string="頻道名稱", required=True, size=10)
    channel_active = fields.Boolean(string="啟用狀態", required=True, default=True)
    channel_port = fields.Many2one(
        "im_livechat.channel",
        string="使用頻道",
    )

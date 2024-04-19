# -*- coding: utf-8 -*-
from odoo import fields, models


class CardReaderModel(models.Model):
    _name = "card_reader"
    _description = "讀卡機裝置資料模型"

    # device_id = fields.Char()
    device_name = fields.Text(string="裝置名稱", required=True)
    device_pos = fields.Text(string="裝置位置", required=False)
    device_uid = fields.Text(string="裝置UID", required=True)
    device_mode = fields.Selection(
        selection=[("Write", "開卡"), ("Read", "讀卡")],
        string="裝置型式",
        required=True,
        default="Read",
    )
    device_connected = fields.Boolean(
        string="裝置啟用", required=True, default=1
    )

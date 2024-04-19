# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class CardInternalGroupModel(models.Model):
    _name = "card.internal_group"
    _description = "內部卡片群組管理"

    internal_group_id = fields.Many2many(
        "card.internal_management", string="內部群組ID", ondelete="cascade"
    )

    internal_group_name = fields.Char(string="群組名稱", size=10, required=True)
    internal_group_remark = fields.Char(string="群組註記")
    internal_group_permissions = fields.One2many(
        "card.internal_permissions",
        "group_permission_id",
        string="許可權限",
    )
    color = fields.Integer("標籤顏色", default=0)

    @api.depends("internal_group_name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.internal_group_name

    @api.model
    def create(self, values):
        if "internal_group_name" in values and not values[
            "internal_group_name"
        ].startswith("(群組)"):
            values["internal_group_name"] = "(群組)" + values["internal_group_name"]
        return super(CardInternalGroupModel, self).create(values)

    def write(self, values):
        if "internal_group_name" in values and not values[
            "internal_group_name"
        ].startswith("(群組)"):
            values["internal_group_name"] = "(群組)" + values["internal_group_name"]
        return super(CardInternalGroupModel, self).write(values)

    def delete_record(self):
        self.ensure_one()
        self.unlink()

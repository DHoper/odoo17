# -*- coding: utf-8 -*-ep
from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class CardInternalManagementModel(models.Model):
    _name = "card.internal_management"
    _description = "內部卡片管理"

    internal_management_cardHolder = fields.Many2one("hr.employee", string="持卡人")
    internal_management_remark = fields.Char(string="卡片註記")
    internal_management_uid = fields.Char(string="卡片UID", size=10, required=True)
    internal_management_active = fields.Boolean(
        string="啟用狀態", required=True, default=True
    )
    internal_management_upload = fields.Boolean(
        string="資料更新狀態", required=True, default=False
    )
    internal_management_validDate = fields.Date(string="卡片效期")
    internal_management_group = fields.Many2many("card.internal_group", string="啟用群組")

    def _get_permissions_type(self):
        for record in self:
            if len(record.internal_management_group) > 0:
                return self._compute_internal_management_permissions()
            else:
                return None

    internal_management_permissions = fields.One2many(
        "card.internal_permissions",
        "permission_id",
        string="卡片權限",
        default=_get_permissions_type,
    )

    @api.depends("internal_management_group")
    def _compute_internal_management_permissions(self):
        for record in self:
            if len(record.internal_management_group) > 0:
                group_permissions = self.env["card.internal_permissions"].search(
                    [
                        (
                            "group_permission_id",
                            "in",
                            record.internal_management_group.ids,
                        )
                    ]
                )
                record.internal_management_permissions = [(6, 0, group_permissions.ids)]
                return [(6, 0, group_permissions.ids)]
            else:
                record.internal_management_permissions = [(5, 0, 0)]

    @api.onchange("internal_management_group")
    def _onchange_internal_management_group(self):
        self._compute_internal_management_permissions()

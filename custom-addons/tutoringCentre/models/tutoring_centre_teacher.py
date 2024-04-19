# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreTeacherModel(models.Model):
    _name = "tutoring_centre.teacher"
    _description = "補習班系統-老師"

    name = fields.Char(string="姓名", required=True)
    is_active = fields.Boolean(string="帳號狀態", required=True, default=True)
    class_groups = fields.Many2many("tutoring_centre.class_group", string="負責班級")
    courses = fields.Many2many("tutoring_centre.course", string="負責課程")
    portal_user = fields.Many2one(
        "res.users",
        string="使用者帳號",
        domain=[("share", "=", False)],
        required=True,
    )
    avatar = fields.Image(string="頭像", compute="_compute_avatar")

    @api.depends("portal_user", "portal_user.image_128")
    def _compute_avatar(self):
        for teacher in self:
            teacher.avatar = teacher.portal_user.image_128 or False

    custom_avatar = fields.Image(string="自定义头像")

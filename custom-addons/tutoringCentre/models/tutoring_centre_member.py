# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, Command
from odoo.tools import email_normalize
from odoo.exceptions import UserError
from odoo.tools.translate import _
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreMember(models.Model):
    _name = "tutoring_centre.member"
    _description = "補習班系統-會員"

    name = fields.Char(string="姓名", required=True)
    email = fields.Char(string="郵箱")
    phone = fields.Char(string="電話", required=True)
    address = fields.Char(string="地址")
    avatar = fields.Image("Image", max_width=128, max_height=128)
    has_current_user = fields.Boolean(
        string="使用現有使用者註冊", default=False, store=False
    )
    is_active = fields.Boolean(string="帳號狀態", required=True, default=True)
    student = fields.One2many(
        "tutoring_centre.student", "member_id", string="學生", required=True
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="對應聯絡人",
        readonly=True,
        ondelete="cascade",
        domain=lambda self: self._get_useable_partners_domain(),
    )
    portal_user = fields.Many2one(
        "res.users",
        string="使用者帳號",
        domain=lambda self: self._get_useable_users_domain(),
        ondelete="cascade",
    )
    is_portal = fields.Boolean("Is Portal", compute="_compute_group_details")
    is_internal = fields.Boolean("Is Internal", compute="_compute_group_details")

    @api.model
    def _get_useable_partners_domain(self):
        records_data = self.env["res.partner"].search([])
        users = self.env["res.users"].search([])
        if users:
            partner_ids = users.mapped("partner_id.id")
        if partner_ids:
            used_partner_ids = [
                record.id for record in records_data if record.id in partner_ids
            ]
            return [
                ("partner_share", "=", True),
                ("id", "not in", used_partner_ids),
                ("email", "!=", False),
            ]

    @api.model
    def _get_useable_users_domain(self):
        records_data = self.search([])
        if records_data:
            _logger.info(records_data)
            _logger.info(records_data.mapped("portal_user.id"))
            portal_user_ids = records_data.mapped("portal_user.id")
        else:
            portal_user_ids = []

        return [
            ("id", "not in", portal_user_ids),
            ("active", "=", True),
            ("share", "=", True),
            ("login", "!=", False),
        ]

    @api.constrains("student")
    def _check_student(self):
        for record in self:
            if not record.student:
                raise exceptions.ValidationError("至少需要有一名學生資料")

    @api.model
    def add_active_channels(self, member_id, channel_ids):
        record = self.browse(member_id)
        if record:
            channels_to_add = [(4, channel_id) for channel_id in channel_ids]
            record.activeChannels = channels_to_add
            return True
        return False

    def _get_useable_im_channel_selections(self):
        usable_im_channel_records = self.env["discuss.channel"].search(
            [("channel_type", "=", "livechat")]
        )
        return [(str(record.id), record.name) for record in usable_im_channel_records]

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            member = super(TutoringCentreMember, self).create(values)
            member.ensure_one()

            if not member.student:
                return member

            if values["has_current_user"] and member.portal_user:
                member.email = member.portal_user.login
                self._create_student_live_channel(member.student)
                return member

            if not member.partner_id:
                existEmail = (
                    self.env["res.partner"]
                    .sudo()
                    .search([("email", "=", values["email"])])
                )
                if existEmail:
                    raise exceptions.ValidationError(
                        "此信箱已註冊為聯絡人，請透過「使用現有使用者註冊」進行註冊"
                    )
                else:
                    member.partner_id = self.env["res.partner"].create(
                        {"name": member.name, "email": member.email, "lang": "zh_TW"}
                    )

            member.portal_user = member.partner_id.with_context(
                active_test=False
            ).user_ids

            if member.is_portal or member.is_internal:
                raise UserError(
                    _(
                        'The partner "%s" already has the portal access.',
                        self.partner_id.name,
                    )
                )

            group_portal = self.env.ref("base.group_portal")
            group_public = self.env.ref("base.group_public")

            user_sudo = member.portal_user.sudo()

            if not user_sudo:
                company = member.partner_id.company_id or self.env.company
                user_sudo = member.sudo().with_company(company.id)._create_user()
                member.portal_user = user_sudo
                member.portal_user.sudo()._change_password(member.phone)

            if not user_sudo.active or not self.is_portal:
                user_sudo.write(
                    {
                        "active": True,
                        "groups_id": [(4, group_portal.id), (3, group_public.id)],
                    }
                )
                user_sudo.partner_id.signup_prepare()
                member.portal_user = user_sudo
                member.portal_user.sudo()._change_password(member.phone)
            # member.with_context(active_test=True)._send_email() #暫不發送密碼認證信
            self._create_student_live_channel(member.student)
            return member

    def write(self, values):
        if "student" not in values:
            return super(TutoringCentreMember, self).write(values)

        original_student = self.student
        member = super(TutoringCentreMember, self).write(values)
        new_records = self.student - original_student
        deleted_records = original_student - self.student
        if new_records:
            self._create_student_live_channel(new_records)
        if deleted_records:
            self._remove_live_channel(deleted_records)
        return member

    def _create_user(self):
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            ._create_user_from_template(
                {
                    "email": email_normalize(self.email),
                    "login": email_normalize(self.email),
                    "partner_id": self.partner_id.id,
                    "company_id": self.env.company.id,
                    "company_ids": [(6, 0, self.env.company.ids)],
                }
            )
        )

    def _send_email(self):
        """send notification email to a new portal user"""
        self.ensure_one()

        template = self.env.ref(
            "tutoringCentre.mail_template_data_tutoring_centre_welcome"
        )
        if not template:
            raise UserError(
                _(
                    'The template "TutoringCentreMember: new user" not found for sending email to the tutoring_centre user.'
                )
            )

        lang = self.portal_user.sudo().lang
        partner = self.portal_user.sudo().partner_id
        portal_url = partner.with_context(
            signup_force_type_in_url="", lang=lang
        )._get_signup_url_for_action()[partner.id]
        partner.signup_prepare()

        template.with_context(
            dbname=self._cr.dbname, portal_url=portal_url, lang=lang
        ).send_mail(self.id, force_send=True)

        return True

    @api.depends("portal_user", "portal_user.groups_id")
    def _compute_group_details(self):
        for record in self:
            user = record.portal_user

            if user and user._is_internal():
                record.is_internal = True
                record.is_portal = False
            elif user and user.has_group("base.group_portal"):
                record.is_internal = False
                record.is_portal = True
            else:
                record.is_internal = False
                record.is_portal = False

    def _create_student_live_channel(self, new_students):
        for record in new_students:
            member_to_add = [
                Command.create(
                    {
                        "partner_id": record.member_id.portal_user.partner_id.id,
                        "is_pinned": False,
                    }
                ),
            ]
            tutoring_livechat = self.env["im_livechat.channel"].search(
                [("category", "=", "tutoringCentre")], limit=1
            )
            channel_vals = {
                "channel_member_ids": member_to_add,
                "channel_type": "livechat",
                "livechat_active": True,
                "livechat_operator_id": 2,
                "livechat_channel_id": tutoring_livechat.id,
                "chatbot_current_step_id": False,
                "anonymous_name": False,
                "country_id": False,
                "name": f"{record.name}{'(' + record.en_name + ')' if record.en_name else ''}",
                "is_persistent": True,
                "outer_user_id": record.id,
            }
            live_channel = (
                self.env["discuss.channel"]
                .with_context(mail_create_nosubscribe=False)
                .sudo()
                .create(channel_vals)
            )
            im_channel = (
                self.env["im_livechat.channel"].sudo().browse(tutoring_livechat.id)
            )
            im_channel.sudo().write({"channel_ids": [(4, live_channel.id)]})
            live_channel.sudo().message_post(
                body=f"(小朋友 : {record.name}{'(' + record.en_name + ')' if record.en_name else ''}) -- 頻道已建立"
            )
            record.sudo().write({"active_channels": live_channel.id})

    def _remove_live_channel(self, removed_students):
        for record in removed_students:
            live_channels = self.env["discuss.channel"].search(
                [
                    ("id", "in", record.active_channels.ids),
                ],
            )
            if live_channels:
                _logger.info(live_channels)
                record.sudo().write({"active_channels": [(3, live_channels)]})
                for channel in live_channels:
                    channel.sudo().write({"active": False})

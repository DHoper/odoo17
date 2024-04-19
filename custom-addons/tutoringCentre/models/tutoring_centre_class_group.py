# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, Command
from datetime import datetime
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreClassGroupModel(models.Model):
    _name = "tutoring_centre.class_group"
    _description = "補習班系統-班級"

    name = fields.Char(string="班級名稱", required=True)
    centre = fields.Selection(
        string="所屬補習班",
        selection=[
            ("fun_apple_SinGuang", "Fun Apple-新光"),
            ("fun_apple_Chongde", "Fun Apple-崇德"),
            ("toeic", "多易"),
            ("study", "學吧"),
        ],
        required=True,
        default=0,
    )
    student = fields.One2many(
        "tutoring_centre.student",
        "class_groups",
        string="學生",
        domain=[("member_id", "!=", False)],
    )
    teacher = fields.Many2many("tutoring_centre.teacher", string="教師")
    class_group_phone = fields.Char(string="班級分機")
    classroom = fields.Char(string="教室位置")
    announcementChannel = fields.Many2one(
        "discuss.channel",
        string="公告頻道",
        domain=[("channel_type", "=", "livechat")],
        readonly=True,
    )
    start_time = fields.Float(string="開始時間", default=0.0)
    end_time = fields.Float(string="結束時間", default=0.0)

    def create(self, values):
        tutoring_livechat = self.env["im_livechat.channel"].search(
            [("category", "=", "tutoringCentre")], limit=1
        )
        if not tutoring_livechat:
            raise exceptions.ValidationError("未找到補習班客服主頻道，請聯絡IT人員")
        class_group = super(TutoringCentreClassGroupModel, self).create(values)
        current_partner = self.env.user.partner_id
        _logger.info("開始創建班級")

        channel_vals = {
            "channel_member_ids": [
                Command.create(
                    {
                        "partner_id": current_partner.id,
                        "is_pinned": True,
                    }
                ),
            ],
            "channel_type": "livechat",
            "livechat_active": True,
            "livechat_operator_id": current_partner.id,
            "livechat_channel_id": tutoring_livechat.id,
            "chatbot_current_step_id": False,
            "anonymous_name": f"{class_group.name}--公告區",
            "country_id": False,
            "name": f"{class_group.name}--公告區",
            "is_persistent": True,
        }

        discuss_channel = (
            self.env["discuss.channel"]
            .with_context(mail_create_nosubscribe=False)
            .sudo()
            .create(channel_vals)
        )
        tutoring_livechat.write({"channel_ids": [(4, discuss_channel.id)]})
        class_group.announcementChannel = discuss_channel.id
        if class_group.teacher:
            self._handle_new_teacher_addition(class_group)
        if class_group.student:
            self._handle_new_student_addition(class_group)

        return class_group

    def _handle_new_teacher_addition(self, class_group):
        for record in class_group.teacher:
            partner_id = record.portal_user.partner_id.id
            if partner_id:

                class_group.announcementChannel.add_members(
                    partner_ids=partner_id, post_joined_message=False
                )

                for student_record in class_group.student:
                    live_channels = self.env["discuss.channel"].search(
                        [
                            ("id", "in", student_record.active_channels.ids),
                        ],
                    )
                    if live_channels:
                        for channel in live_channels:
                            channel.sudo().add_members(
                                partner_ids=partner_id,
                                post_joined_message=False,
                            )

    def _handle_new_student_addition(self, class_group):
        # self._create_live_channel(class_group.student, class_group)
        for record in class_group.student:
            partner_id = record.member_id.portal_user.partner_id.id
            if partner_id:
                class_group.announcementChannel.add_members(
                    partner_ids=partner_id, post_joined_message=False
                )

    def unlink(self):
        for class_group in self:
            if class_group.announcementChannel:
                channels = self.env["discuss.channel"].search(
                    [("livechat_channel_id", "=", class_group.announcementChannel.id)]
                )
                for channel in channels:
                    channel.sudo().write({"active": False})
                class_group.announcementChannel.sudo().unlink()
        return super(TutoringCentreClassGroupModel, self).unlink()

    def write(self, vals):
        original_student = self.student
        original_teacher = self.teacher
        res = super(TutoringCentreClassGroupModel, self).write(vals)
        if "student" in vals:
            new_records = self.student - original_student
            deleted_records = original_student - self.student

            new_students = self.env["tutoring_centre.student"].browse(new_records.ids)
            if deleted_records:
                # self._remove_live_channel(deleted_records)
                deleted_ids = [
                    record.member_id.portal_user.partner_id.id
                    for record in deleted_records
                ]
            student_member_ids = self.student.mapped("member_id").ids

            deleted_ids = [
                record.member_id.portal_user.partner_id.id
                for record in deleted_records
                if record.member_id.id
                not in student_member_ids  # 避免有重複ID(同家長不同學生)
            ]
            if deleted_ids:
                self._remove_members_from_channel_member(deleted_ids)

            if new_records:
                # self._create_live_channel(new_students)
                for record in new_students:
                    partner_id = record.member_id.portal_user.partner_id.id
                    if partner_id:
                        self.announcementChannel.add_members(
                            partner_ids=partner_id, post_joined_message=False
                        )
        if "teacher" in vals:
            new_teacher_records = self.teacher - original_teacher
            deleted_records = original_teacher - self.teacher

            deleted_teacher_ids = [
                record.portal_user.partner_id.id for record in deleted_records
            ]
            if deleted_teacher_ids:
                self._remove_members_from_channel_member(deleted_teacher_ids)
                for student in self.student:
                    for student_channel in student.active_channels:
                        self._remove_members_from_student_channel_member(
                            student_channel.id, deleted_teacher_ids
                        )

            new_teachers = self.env["tutoring_centre.teacher"].browse(
                new_teacher_records.ids
            )
            if new_teachers:
                _logger.info("<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                _logger.info(new_teachers)
                for record in new_teachers:
                    teacher_partner_id = record.portal_user.partner_id.id
                    if teacher_partner_id:
                        self.announcementChannel.sudo().add_members(
                            partner_ids=teacher_partner_id, post_joined_message=False
                        )
                        for student_record in self.student:
                            _logger.info(student_record.active_channels.ids)
                            live_channels = (
                                self.env["discuss.channel"]
                                .sudo()
                                .search(
                                    [
                                        (
                                            "id",
                                            "in",
                                            student_record.active_channels.ids,
                                        ),
                                    ],
                                )
                            )
                            _logger.info(f"live_channelsssss{live_channels}")
                            if live_channels:
                                live_channels.sudo().add_members(
                                    partner_ids=teacher_partner_id,
                                    post_joined_message=False,
                                )
        else:
            return super(TutoringCentreClassGroupModel, self).write(vals)
        return res

    def _remove_members_from_channel_member(self, ids):
        for id in ids:
            channel_member = self.env["discuss.channel.member"].search(
                [
                    ("partner_id", "=", id),
                    ("channel_id", "=", self.announcementChannel.id),
                ]
            )
            if channel_member:
                channel_member.sudo().unlink()

    def _remove_members_from_student_channel_member(self, student_channel_id, ids):
        for id in ids:
            channel_member = self.env["discuss.channel.member"].search(
                [
                    ("partner_id", "=", id),
                    ("channel_id", "=", student_channel_id),
                ]
            )
            if channel_member:
                channel_member.sudo().unlink()

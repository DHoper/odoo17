# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions, Command
from datetime import datetime, timedelta
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreCourseModel(models.Model):
    _name = "tutoring_centre.course"
    _description = "補習班系統-課程"

    name = fields.Char(string="課程名稱", required=True)
    category = fields.Selection(
        string="課程類型",
        selection=[
            ("english", "英文"),
            ("stem", "數理"),
            ("humanities", "文科"),
            ("art", "才藝"),
        ],
        required=True,
        default="english",
    )
    student = fields.Many2many(
        "tutoring_centre.student",
        string="學生",
        domain=[("member_id", "!=", False)],
    )
    teacher = fields.Many2many("tutoring_centre.teacher", string="任課教師", required=True)
    announcements = fields.One2many(
        "tutoring_centre.course_announcement", "course_id", string="課程公告"
    )
    promote_intro = fields.Text("課程介紹(推廣)")
    notes = fields.One2many(
        "tutoring_centre.course_note", "course_id", string="課堂註記事項"
    )
    course_phone = fields.Char(string="課程分機")
    classroom = fields.Char(string="教室位置")

    start_date = fields.Date("課程開始日", default=fields.Date.today(), required=True)
    end_date = fields.Date("課程結束日", required=True)

    def _default_dates(self, startTime, endTime):
        return [
            {"day_of_week": day, "start_time": startTime, "end_time": endTime}
            for day in [
                "sunday",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ]
        ]

    dates = fields.One2many(
        "tutoring_centre.course_dates_config",
        "course_id",
        string="上課時間",
        default=lambda self: self._default_dates(
            "18",
            "20",
        ),
        required=True,
    )

    @api.constrains("teacher")
    def check_required(self):
        for record in self:
            if not record.teacher:
                raise exceptions.ValidationError("教師欄位不得為空！")

    def create(self, values):
        tutoring_livechat = self.env["im_livechat.channel"].search(
            [("category", "=", "tutoringCentre")], limit=1
        )
        if not tutoring_livechat:
            raise exceptions.ValidationError("未找到補習班客服主頻道，請聯絡IT人員")
        course = super(TutoringCentreCourseModel, self).create(values)

        if course.teacher:
            self._handle_new_teacher_addition(course)

        return course

    def _handle_new_teacher_addition(self, course):
        for record in course.teacher:
            partner_id = record.portal_user.partner_id.id
            if partner_id:
                for student_record in course.student:
                    live_channels = (
                        self.env["discuss.channel"]
                        .sudo()
                        .search(
                            [
                                ("id", "in", student_record.active_channels.ids),
                            ],
                        )
                    )
                    if live_channels:
                        for channel in live_channels:
                            channel.sudo().add_members(
                                partner_ids=partner_id,
                                post_joined_message=False,
                            )

    def unlink(self):
        for course in self:
            if course.student:
                teacher_ids = []
                for teacher in course.teacher:
                    teacher_partner_id = teacher.portal_user.partner_id.id
                    teacher_ids.append(teacher_partner_id)
                for student in course.student:
                    for student_channel in student.active_channels:
                        self._remove_members_from_student_channel_member(
                            student_channel.id, teacher_ids
                        )

        return super(TutoringCentreCourseModel, self).unlink()

    def write(self, vals):
        original_student = self.student
        original_teacher = self.teacher
        res = super(TutoringCentreCourseModel, self).write(vals)
        if "student" in vals:
            new_records = self.student - original_student
            deleted_records = original_student - self.student
            if new_records:
                for student in new_records:
                    live_channels = (
                        self.env["discuss.channel"]
                        .sudo()
                        .search(
                            [
                                (
                                    "id",
                                    "in",
                                    student.active_channels.ids,
                                ),
                            ],
                        )
                    )
                    if live_channels:
                        for teacher in self.teacher:
                            teacher_partner_id = teacher.portal_user.partner_id.id
                            live_channels.sudo().add_members(
                                partner_ids=teacher_partner_id,
                                post_joined_message=False,
                            )
            if deleted_records:
                for student in deleted_records:
                    teacher_ids = []
                    for teacher in self.teacher:
                        teacher_partner_id = teacher.portal_user.partner_id.id
                        teacher_ids.append(teacher_partner_id)
                    for student_channel in student.active_channels:
                        self._remove_members_from_student_channel_member(
                            student_channel.id, teacher_ids
                        )

        if "teacher" in vals:
            new_teacher_records = self.teacher - original_teacher
            deleted_teacher_records = original_teacher - self.teacher

            deleted_teacher_ids = [
                record.portal_user.partner_id.id for record in deleted_teacher_records
            ]
            if deleted_teacher_ids:
                for student in self.student:
                    for student_channel in student.active_channels:
                        self._remove_members_from_student_channel_member(
                            student_channel.id, deleted_teacher_ids
                        )

            new_teachers = self.env["tutoring_centre.teacher"].browse(
                new_teacher_records.ids
            )
            if new_teachers:
                for record in new_teachers:
                    teacher_partner_id = record.portal_user.partner_id.id
                    if teacher_partner_id:
                        for student_record in self.student:
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
                            if live_channels:
                                live_channels.sudo().add_members(
                                    partner_ids=teacher_partner_id,
                                    post_joined_message=False,
                                )
        else:
            return super(TutoringCentreCourseModel, self).write(vals)
        return res

    def _remove_members_from_student_channel_member(self, student_channel_id, ids):
        pass
        # for id in ids:
        #     channel_member = self.env["discuss.channel.member"].search(
        #         [
        #             ("partner_id", "=", id),
        #             ("channel_id", "=", student_channel_id),
        #         ]
        #     )
        #     if channel_member:
        #         channel_member.sudo().unlink()


class TutoringCentreCourseDatesModel(models.Model):
    _name = "tutoring_centre.course_dates_config"
    _description = "上課時間"

    is_active = fields.Boolean(string="啟用", default=True)
    course_id = fields.Many2one(
        "tutoring_centre.course",
        string="所屬課程",
        ondelete="cascade",
    )
    day_of_week = fields.Selection(
        [
            ("sunday", "星期日"),
            ("monday", "星期一"),
            ("tuesday", "星期二"),
            ("wednesday", "星期三"),
            ("thursday", "星期四"),
            ("friday", "星期五"),
            ("saturday", "星期六"),
        ],
        string="日期(星期)",
        required=True,
    )

    _hours = [(f"{i:02d}", f"{i:02d}:00 {'AM' if i < 12 else 'PM'}") for i in range(24)]
    start_time = fields.Selection(_hours, string="開始時間")
    end_time = fields.Selection(
        _hours,
        string="結束時間",
    )

    @api.onchange("is_active")
    def _set_time_null(self):
        if (
            self.is_active is False
        ):  # 若該field有設置default值 則將會僅在介面(視覺)上起作用，資料庫還是會被存入default值
            self.start_time = False
            self.end_time = False

    @api.constrains("day_of_week", "course_id")
    def _check_unique_day_of_week_per_config(self):
        for record in self:
            if record.day_of_week and record.course_id:
                existing_records = self.search(
                    [
                        ("day_of_week", "=", record.day_of_week),
                        ("course_id", "=", record.course_id.id),
                        ("id", "!=", record.id),
                    ]
                )
                if existing_records:
                    raise exceptions.ValidationError("日期(星期)不可重複！")

    @api.constrains("end_time", "start_time")
    def _check_end_time(self):
        for record in self:
            if (
                record.end_time
                and record.start_time
                and int(record.end_time) <= int(record.start_time)
            ):
                raise exceptions.ValidationError("上課時間的結束時間必須晚於開始時間！")


class TutoringCentreCourseNote(models.Model):
    _name = "tutoring_centre.course_note"
    _description = "課程註記事項"

    start_date = fields.Date("開始日期", default=fields.Date.today())
    end_date = fields.Date(
        "結束日期",
        default=lambda self: (datetime.today() + timedelta(days=7)).strftime(
            "%Y-%m-%d"
        ),
    )
    context = fields.Char("內容")
    course_id = fields.Many2one(
        "tutoring_centre.course",
        string="所屬課程",
        required=True,
        readonly=True,
        ondelete="cascade",
    )

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
    teacher = fields.Many2many("tutoring_centre.teacher", string="教師", required=True)
    announcements = fields.One2many(
        "tutoring_centre.course_announcement", "course_id", string="課程公告"
    )
    notes = fields.One2many(
        "tutoring_centre.course_note", "course_id", string="課堂註記事項"
    )
    course_phone = fields.Char(string="課程分機")
    classroom = fields.Char(string="教室位置")

    start_date = fields.Date("課程開始日", default=fields.Date.today(), required=True)
    end_date = fields.Date("課程結束日", default=fields.Date.today(), required=True)

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
    )


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
                raise exceptions.ValidationError("時間許可的結束時間必須大於開始時間！")


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

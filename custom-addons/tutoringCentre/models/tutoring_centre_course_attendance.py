from odoo import models, fields, api
from odoo.exceptions import ValidationError
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class CourseAttendance(models.Model):
    _name = "tutoring_centre.course_attendance"
    _description = "班級點名表"

    course_id = fields.Many2one("tutoring_centre.course", string="班級", required=True)
    teacher_ids = fields.Many2many(
        related="course_id.teacher", string="可選老師", store=False
    )
    checking_teacher = fields.Many2one(
        "tutoring_centre.teacher",
        string="負責老師",
        required=True,
        domain="[('id', 'in', teacher_ids)]",
    )
    attendance_line_ids = fields.One2many(
        "tutoring_centre.course_attendance_line",
        "course_attendance_id",
        string="學生出席紀錄",
        required=True,
    )
    total_students = fields.Integer(
        string="應到人數", compute="_compute_attendance_data"
    )
    attended_students = fields.Integer(
        string="實到人數", compute="_compute_attendance_data"
    )
    absent_students = fields.Integer(
        string="未到人數", compute="_compute_attendance_data"
    )
    date = fields.Date(string="日期", default=fields.Date.today(), required=True)
    start_time = fields.Datetime("開始時間", default=fields.Datetime.now())
    end_time = fields.Datetime("結束時間")

    def _get_teacher_domain(self):
        domain = []
        if self.course_id:
            teacher_ids = self.course_id.teacher.ids if self.course_id.teacher else []
            domain.append(("id", "in", teacher_ids))
        return domain

    @api.depends("attendance_line_ids", "attendance_line_ids.attended")
    def _compute_attendance_data(self):
        for record in self:
            record.total_students = len(record.course_id.student)
            record.attended_students = len(
                record.attendance_line_ids.filtered(lambda line: line.attended)
            )
            record.absent_students = record.total_students - record.attended_students

    @api.model
    def default_get(self, fields):
        defaults = super(CourseAttendance, self).default_get(fields)
        course_id = self.env.context.get("course_id")
        if course_id:
            course = self.env["tutoring_centre.course"].browse(course_id)
            defaults["course_id"] = course.id
            student_ids = course.student.ids
            defaults["attendance_line_ids"] = [
                (
                    0,
                    0,
                    {"student_id": student_id},
                )
                for student_id in student_ids
            ]
        return defaults

    def create(self, values):
        attendance = super(CourseAttendance, self).create(values)
        _logger.info(values)
        # students = []
        for attendance_line in attendance.attendance_line_ids:
            if attendance_line.attended:
                attendance_line.start_time = attendance.start_time
                attendance_line.end_time = attendance.end_time

        return attendance

    def write(self, values):
        super(CourseAttendance, self).write(values)
        if "start_time" in values or "end_time" in values:
            for attendance_line in self.attendance_line_ids.filtered(
                lambda line: line.attended
            ):
                if "start_time" in values:
                    attendance_line.start_time = values["start_time"]
                if "end_time" in values:
                    attendance_line.end_time = values["end_time"]

    def action_set_end_time(self):
        self.end_time = fields.datetime.now()
        for attendance_line in self.attendance_line_ids:
            attendance_line.end_time = self.end_time

    @api.constrains("course_id", "date")
    def _check_unique_attendance_per_day(self):
        for attendance in self:
            if attendance.course_id and attendance.date:
                existing_attendance = self.env[
                    "tutoring_centre.course_attendance"
                ].search(
                    [
                        ("course_id", "=", attendance.course_id.id),
                        ("date", ">=", attendance.date),
                        ("id", "!=", attendance.id),
                    ]
                )
                if existing_attendance:
                    if existing_attendance[0].date == attendance.date:
                        raise ValidationError("此課程已經存在今日的點名表紀錄。")


class AttendanceLine(models.Model):
    _name = "tutoring_centre.course_attendance_line"
    _description = "單筆學生出席紀錄"

    course_attendance_id = fields.Many2one(
        "tutoring_centre.course_attendance",
        string="對應點名表",
        ondelete="cascade",
        readonly=True,
    )
    course_id = fields.Integer(
        related="course_attendance_id.course_id.id",
        string="對應班級ID",
        store=True,
        required=True,
    )
    course_name = fields.Char(
        related="course_attendance_id.course_id.name",
        string="對應班級",
    )
    checking_teacher = fields.Many2one(
        "tutoring_centre.teacher",
        related="course_attendance_id.checking_teacher",
        string="對應點名老師",
        domain="[('id', 'in', teacher_ids)]",
    )
    student_id = fields.Many2one(
        "tutoring_centre.student",
        string="學生",
        ondelete="cascade",
    )
    attended = fields.Boolean(string="出席狀況", default=True)
    remark = fields.Char("備註事由")
    date = fields.Date(
        string="日期",
        default=fields.Date.today(),
        required=True,
        related="course_attendance_id.date",
    )
    start_time = fields.Datetime(string="上課時間")
    end_time = fields.Datetime(string="下課時間")

    # @api.depends("course_attendance_id")
    # def _default_start_time(self):
    #     for record in self:
    #         if record.course_attendance_id:
    #             record.start_time = record.course_attendance_id.start_time

    # @api.depends("course_attendance_id")
    # def _default_end_time(self):
    #     for record in self:
    #         if record.course_attendance_id:
    #             record.end_time = record.course_attendance_id.end_time

    @api.onchange("attended")
    def _set_time_null(self):
        if self.attended is False:
            self.start_time = False
            self.end_time = False

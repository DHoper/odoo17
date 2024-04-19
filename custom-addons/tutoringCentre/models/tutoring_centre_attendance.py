from odoo import models, fields, api
from odoo.exceptions import ValidationError
from markupsafe import Markup
import logging

_logger = logging.getLogger(__name__)


class ClassGroupAttendance(models.Model):
    _name = "tutoring_centre.class_group_attendance"
    _description = "班級點名表"

    class_group_id = fields.Many2one("tutoring_centre.class_group", string="班級", required=True)
    teacher_ids = fields.Many2many(
        related="class_group_id.teacher", string="可選老師", store=False
    )
    checking_teacher = fields.Many2one(
        "tutoring_centre.teacher",
        string="負責老師",
        required=True,
        domain="[('id', 'in', teacher_ids)]",
    )
    attendance_line_ids = fields.One2many(
        "tutoring_centre.class_group_attendance_line",
        "class_group_attendance_id",
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
    start_time = fields.Datetime("開始時間", default=fields.Datetime.now())
    end_time = fields.Datetime("結束時間")

    def _get_teacher_domain(self):
        domain = []
        if self.class_group_id:
            teacher_ids = self.class_group_id.teacher.ids if self.class_group_id.teacher else []
            domain.append(("id", "in", teacher_ids))
        return domain

    @api.depends("attendance_line_ids", "attendance_line_ids.attended")
    def _compute_attendance_data(self):
        for record in self:
            record.total_students = len(record.class_group_id.student)
            record.attended_students = len(
                record.attendance_line_ids.filtered(lambda line: line.attended)
            )
            record.absent_students = record.total_students - record.attended_students

    @api.model
    def default_get(self, fields):
        defaults = super(ClassGroupAttendance, self).default_get(fields)
        class_group_id = self.env.context.get("class_group_id")
        if class_group_id:
            class_group = self.env["tutoring_centre.class_group"].browse(class_group_id)
            defaults["class_group_id"] = class_group.id
            student_ids = class_group.student.ids
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
        attendance = super(ClassGroupAttendance, self).create(values)
        students = []
        for attendance_line in attendance.attendance_line_ids:
            if attendance_line.attended == True:
                attendance_line.start_time = attendance.start_time
                attendance_line.end_time = attendance.end_time
                students.append(attendance_line.student_id)
        self.roll_call(attendance.class_group_id.id, students)
        return attendance

    def write(self, values):
        super(ClassGroupAttendance, self).write(values)
        if "start_time" in values or "end_time" in values:
            for attendance_line in self.attendance_line_ids.filtered(
                lambda line: line.attended
            ):
                if "start_time" in values:
                    attendance_line.start_time = values["start_time"]
                if "end_time" in values:
                    attendance_line.end_time = values["end_time"]

    @api.model
    def roll_call(self, class_group_id, students):
        current_partner_id = self.env.user.partner_id
        class_group = self.env["tutoring_centre.class_group"].sudo().browse(class_group_id)
        for student in students:
            domain = [
                (
                    "id",
                    "in",
                    student.active_channels.ids,
                ),
                (
                    "id",
                    "!=",
                    class_group.announcementChannel.id,
                ),
            ]
            channel = self.env["discuss.channel"].search(domain)
            message = f"爸爸媽媽您好<br/>{student.name}小朋友已經在我們{class_group.name}班上完成點名<br/>請您放心。"
            channel.message_post(
                body=Markup(f"<p>{message}</p>"),
                author_id=current_partner_id.id,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )

    @api.constrains("class_group_id", "start_time")
    def _check_unique_attendance_per_day(self):
        for attendance in self:
            if attendance.class_group_id and attendance.start_time:
                attendance_date = attendance.start_time.date()
                existing_attendance = self.env[
                    "tutoring_centre.class_group_attendance"
                ].search(
                    [
                        ("class_group_id", "=", attendance.class_group_id.id),
                        ("start_time", ">=", attendance_date),
                        ("id", "!=", attendance.id),
                    ]
                )
                if existing_attendance:
                    if existing_attendance[0].start_time.date() == attendance_date:
                        raise ValidationError("此課程已經存在今日的點名表紀錄。")


class AttendanceLine(models.Model):
    _name = "tutoring_centre.class_group_attendance_line"
    _description = "單筆學生出席紀錄"

    class_group_attendance_id = fields.Many2one(
        "tutoring_centre.class_group_attendance",
        string="對應點名表",
        ondelete="cascade",
        readonly=True,
    )
    class_group_name = fields.Char(
        related="class_group_attendance_id.class_group_id.name",
        string="對應班級",
        readonly=True,
    )
    student_id = fields.Many2one(
        "tutoring_centre.student", string="學生", required=True, ondelete="cascade",
    )
    attended = fields.Boolean(string="出席狀況", default=True)
    remark = fields.Char("備註事由")
    start_time = fields.Datetime(string="上課時間")
    end_time = fields.Datetime(string="下課時間")

    # @api.depends("class_group_attendance_id")
    # def _default_start_time(self):
    #     for record in self:
    #         if record.class_group_attendance_id:
    #             record.start_time = record.class_group_attendance_id.start_time

    # @api.depends("class_group_attendance_id")
    # def _default_end_time(self):
    #     for record in self:
    #         if record.class_group_attendance_id:
    #             record.end_time = record.class_group_attendance_id.end_time

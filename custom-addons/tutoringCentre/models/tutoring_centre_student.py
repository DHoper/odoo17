from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreStudent(models.Model):
    _name = "tutoring_centre.student"
    _description = "補習班系統-會員-學生"

    name = fields.Char(string="姓名")
    en_name = fields.Char(string="英文名")
    avatar = fields.Image("Image", max_width=128, max_height=128)
    gender = fields.Selection(
        string="性別",
        selection=[
            ("male", "男"),
            ("female", "女"),
        ],
    )
    member_id = fields.Many2one("tutoring_centre.member", string="會員")
    parent_name = fields.Char(related="member_id.name", string="家長姓名")
    parent_phone = fields.Char(
        string="家長電話", readonly=True, compute="_compute_parent_phone"
    )
    class_groups = fields.Many2one(
        "tutoring_centre.class_group", string="分班", readonly=True
    )
    courses = fields.Many2many("tutoring_centre.course", string="課程", readonly=True)
    active_channels = fields.Many2one(
        "discuss.channel",
        string="啟用頻道",
        readonly=True,
        ondelete="cascade",
    )
    is_arrival = fields.Boolean(default=False)
    # is_departure = fields.Boolean(default=False, store=False)

    def unlink(self):
        for student in self:
            if not student.member_id:
                return super(TutoringCentreStudent, self).unlink()
            if student.active_channels:
                for channel in student.active_channels:
                    channel.active = False
        return super(TutoringCentreStudent, self).unlink()

    @api.depends("member_id", "member_id.phone")
    def _compute_parent_phone(self):
        for student in self:
            if student.member_id and student.member_id.phone:
                student.parent_phone = student.member_id.phone
            else:
                student.parent_phone = False

    def write(self, vals):
        if "member_id" not in vals:
            return super(TutoringCentreStudent, self).write(vals)
        if vals["member_id"] == False:
            vals["class_groups"] = [(5, 0, 0)]
        return super(TutoringCentreStudent, self).write(vals)

    def _reset_arrival_corn(self):
        students = self.env["tutoring_centre.student"].sudo().search()
        if students:
            students.write({"is_arrival": False})

    def action_arrival_notice(self):
        current_partner_id = self.env.user.partner_id
        current_time = datetime.now()
        exist_record = self.env["tutoring_centre.student_arrival"].search(
            [("date", "=", current_time.date()), ("student_id", "=", self.id)]
        )
        if exist_record:
            exist_record.unlink()

        arrival_record = self.env["tutoring_centre.student_arrival"].create(
            {
                "date": current_time.date(),
                "arrival_time": current_time,
                "student_id": self.id,
            }
        )

        # 發送到校通知
        self.active_channels.sudo().message_post(
            body=f"{self.name}小朋友目前已抵達補習班，請您放心。",
            author_id=current_partner_id.id,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )

        self.is_arrival = True

        return arrival_record

    def action_departure_notice(self):
        current_partner_id = self.env.user.partner_id
        current_time = datetime.now()

        # 創建新的離校紀錄
        departure_record = self.env["tutoring_centre.student_arrival"].search(
            [("date", "=", current_time.date()), ("student_id", "=", self.id)]
        )
        if departure_record:
            departure_record.departure_time = current_time
        else:
            raise ValidationError(("查無本日到校紀錄，請聯絡IT人員"))

        # 發送離校通知
        self.active_channels.sudo().message_post(
            body=f"{self.name}小朋友目前已離開補習班，請多加留意！",
            author_id=current_partner_id.id,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )

        self.is_arrival = False

        return departure_record

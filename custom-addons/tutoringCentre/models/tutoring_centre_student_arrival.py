from odoo import fields, models, api
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class TutoringCentreStudentArrival(models.Model):
    _name = "tutoring_centre.student_arrival"
    _description = "補習班系統-會員-學生-到校紀錄"

    date = fields.Date("日期")
    arrival_time = fields.Datetime(string="到校時間")
    departure_time = fields.Datetime(string="離校校時間")
    student_id = fields.Many2one(
        "tutoring_centre.student",
        "所屬學生",
        required=True,
        ondelete="cascade",
    )

    # _sql_constraints = [
    #     (
    #         "unique_date_student",
    #         "UNIQUE(date, student_id)",
    #         "每個學生一天只能有一筆到校紀錄",
    #     )
    # ]

    # @api.constrains("date", "student_id")
    # def check_unique_arrival(self):
    #     for record in self:
    #         domain = [
    #             ("date", "=", record.date),
    #             ("student_id", "=", record.student_id.id),
    #         ]
    #         count = self.search_count(domain)
    #         if count > 1:
    #             raise ValidationError("每個學生一天只能有一筆到校紀錄")

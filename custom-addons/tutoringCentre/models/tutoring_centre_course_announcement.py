from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CourseAnnouncement(models.Model):
    _name = "tutoring_centre.course_announcement"
    _description = "課程公告"

    title = fields.Char("標題")
    context = fields.Text("內容", required=True)
    course_id = fields.Many2one(
        "tutoring_centre.course",
        string="所屬課程",
        required=True,
        ondelete="cascade",
        default=lambda self: self._context.get("course_id", False),
    )

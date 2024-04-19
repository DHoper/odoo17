from odoo import fields, models, api


class ParentPickTransient(models.TransientModel):
    _name = "tutor_talk.parent_pick"
    _description = "TutorTalk-家長接送_瞬態"

    student = fields.Many2many("tutoring_centre.student")

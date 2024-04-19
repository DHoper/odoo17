from odoo.http import request, route, Controller
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreMemberController(Controller):
    @route("/tutoringCentre/api/update_member", type="json", auth="public", csrf=False)
    def _update_member(self, member_id, updateData):
        if not member_id:
            return False

        data_to_write = {}
        if updateData.get("name"):
            data_to_write["name"] = updateData["name"]
        if updateData.get("email"):
            data_to_write["email"] = updateData["email"]
        if updateData.get("phone"):
            data_to_write["phone"] = updateData["phone"]
        if updateData.get("address"):
            data_to_write["address"] = updateData["address"]
        if updateData.get("avatar"):
            data_to_write["avatar"] = updateData["avatar"]

        member = request.env["tutoring_centre.member"].sudo().browse(member_id)
        if not member:
            return f"未找到該會員 : {member_id}"

        _logger.info(data_to_write)

        member.write(data_to_write)

    @route("/tutoringCentre/api/update_student", type="json", auth="public", csrf=False)
    def _update_student(self, student_id, updateData):
        if not student_id:
            return False

        data_to_write = {}
        if updateData.get("name"):
            data_to_write["name"] = updateData["name"]
        if updateData.get("en_name"):
            data_to_write["en_name"] = updateData["en_name"]
        if updateData.get("avatar"):
            data_to_write["avatar"] = updateData["avatar"]

        student = request.env["tutoring_centre.student"].sudo().browse(student_id)
        if not student:
            return f"未找到該學生 : {student_id}"

        student.write(data_to_write)

    @route("/tutoringCentre/api/memberInfo", type="json", auth="public", cors="*")
    def _get_member_info(self, userID):
        member = (
            request.env["tutoring_centre.member"]
            .sudo()
            .search([("portal_user", "=", userID)], limit=1)
        )

        if not member:
            return False

        student_data = member.student.read()
        for student in student_data:
            student["class_groups"] = member.student.filtered(
                lambda s: s.id == student["id"]
            ).class_groups.read()
            courses = []
            for course_id in student["courses"]:
                course = request.env["tutoring_centre.course"].sudo().browse(course_id)
                course = course.read()[0]
                filtered_course = {}
                filtered_course["id"] = course["id"]
                filtered_course["name"] = course["name"]
                if course["teacher"]:
                    teacher = (
                        request.env["tutoring_centre.teacher"]
                        .sudo()
                        .browse(course["teacher"])
                    )
                    filtered_course["teacher"] = teacher.read()
                else:
                    filtered_course["teacher"] = False
                filtered_course["category"] = course["category"]
                filtered_course["classroom"] = course["classroom"]
                filtered_course["course_phone"] = course["course_phone"]
                filtered_course["start_date"] = course["start_date"]
                filtered_course["end_date"] = course["end_date"]
                if course["dates"]:
                    dates = (
                        request.env["tutoring_centre.course_dates_config"]
                        .sudo()
                        .browse(course["dates"])
                    )
                    filtered_course["dates"] = dates.read()
                else:
                    filtered_course["dates"] = False
                if course["notes"]:
                    notes = (
                        request.env["tutoring_centre.course_note"]
                        .sudo()
                        .browse(course["notes"])
                    )
                    filtered_course["notes"] = notes.read()
                else:
                    filtered_course["notes"] = False
                courses.append(filtered_course)
            student["courses"] = courses
            member_values = member.read()[0]
            member_values["student"] = student_data
            member_values["partner_id"] = member.portal_user.partner_id.id

            return member_values

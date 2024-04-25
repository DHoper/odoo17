from odoo.http import request, route, Controller
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreCourseController(Controller):
    @route(
        "/tutoringCentre/api/get_courses_announcements",
        type="json",
        auth="public",
    )
    def _get_courses_announcements(self, course_ids):
        if not course_ids:
            return False
        announcements = (
            request.env["tutoring_centre.course_announcement"]
            .sudo()
            .search([("course_id", "in", course_ids)])
        )
        if announcements:
            return announcements.read()
        else:
            return "未找到課程公告資料"

    @route(
        "/tutoringCentre/api/get_all_course",
        type="json",
        auth="public",
    )
    def _get_all_course(self):
        raw_courses = request.env["tutoring_centre.course"].sudo().search([])
        courses_data = raw_courses.read() if raw_courses else None
        if not courses_data:
            return []

        courses = []
        for course in courses_data:
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
            filtered_course["promote_intro"] = course["promote_intro"]
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

        return courses

    @route(
        "/tutoringCentre/api/get_courses_attendances",
        type="json",
        auth="public",
    )
    def _get_courses_attendances(self, student_id, year, month):
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return {"error": "年月格式錯誤"}

        attendances = (
            request.env["tutoring_centre.course_attendance_line"]
            .sudo()
            .search(
                [
                    ("student_id", "=", student_id),
                    # ("end_time", "!=", None),
                    # ("start_time", "<=", to_date),
                ]
            )
        )

        if not attendances:
            return False

        attendance_records = []
        for attendance in attendances:
            attendance_records.append(attendance.read()[0])
        return attendance_records

    @route(
        "/tutoringCentre/api/get_student_arrivals",
        type="json",
        auth="public",
    )
    def _get_student_arrivals(self, student_id, year, month):
        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return {"error": "年月格式錯誤"}

        arrivals = (
            request.env["tutoring_centre.student_arrival"]
            .sudo()
            .search(
                [
                    ("student_id", "=", student_id),
                ]
            )
        )

        if not arrivals:
            return False

        arrival_records = []
        for arrival in arrivals:
            arrival_records.append(
                {
                    "arrival_time": arrival.arrival_time,
                    "departure_time": arrival.departure_time,
                    "date": arrival.date,
                }
            )
        return arrival_records

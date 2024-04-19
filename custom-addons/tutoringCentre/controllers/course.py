from odoo.http import request, route, Controller
from datetime import datetime, timedelta
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

        start_date = datetime(year, month, 1)
        end_date = start_date.replace(
            month=month % 12 + 1, year=year if month < 12 else year + 1, day=1
        )

        attendances = (
            request.env["tutoring_centre.course_attendance_line"]
            .sudo()
            .search(
                [
                    ("student_id", "=", student_id),
                    # ("end_time", "!=", None),
                    ("start_time", ">=", start_date.strftime("%Y-%m-%d %H:%M:%S")),
                    ("start_time", "<", end_date.strftime("%Y-%m-%d %H:%M:%S")),
                ]
            )
        )
        if not attendances:
            return False

        return attendances.read()

    # @route(
    #     "/tutoringCentre/api/get_today_courses_attendance",
    #     type="json",
    #     auth="public",
    # )
    # def _get_today_courses_attendance(self, student_id):
    #     today_date = datetime.now().date()

    #     attendances = (
    #         request.env["tutoring_centre.course_attendance_line"]
    #         .sudo()
    #         .search(
    #             [
    #                 ("student_id", "=", student_id),
    #             ]
    #         )
    #     )

    #     if not attendances:
    #         return {"error": "未找到指定條件之出席紀錄"}

    #     attendance_records = []

    #     for attendance in attendances:
    #         attendance_data = attendance.read()
    #         if attendance_data:
    #             first_attendance = attendance_data[0]
    #             start_time = first_attendance.get("start_time")
    #             end_time = first_attendance.get("end_time")

    #             if start_time:
    #                 start_time += timedelta(hours=8)
    #                 first_attendance["start_time"] = start_time

    #             if end_time:
    #                 end_time += timedelta(hours=8)
    #                 first_attendance["end_time"] = end_time

    #             if start_time and start_time.date() == today_date:
    #                 attendance_records.append(first_attendance)

    #     return attendance_records

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

        start_date = datetime(year, month, 1)
        end_date = start_date.replace(
            month=month % 12 + 1, year=year if month < 12 else year + 1, day=1
        )

        arrivals = (
            request.env["tutoring_centre.student_arrival"]
            .sudo()
            .search(
                [
                    ("student_id", "=", student_id),
                    ("date", ">=", start_date),
                    ("date", "<", end_date),
                ]
            )
        )
        if not arrivals:
            return False

        return arrivals.read()


# @route(
#     "/tutoringCentre/api/get_courses",
#     type="json",
#     auth="public",
# )
# def _get_courses_announcements(self, course_ids):
#     if not course_ids:
#         return False
#     courses = (
#         request.env["tutoring_centre.course_announcement"]
#         .sudo()
#         .search([("course_id", "in", course_ids)])
#     )
#     _logger.info(course_ids)
#     _logger.info(announcements)
#     if announcements:
#         return announcements.read()
#     else:
#         return "未找到課程公告資料"

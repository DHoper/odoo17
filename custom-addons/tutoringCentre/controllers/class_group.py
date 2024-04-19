from odoo.http import request, route, Controller
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class TutoringCentreClassGroupController(Controller):
    # @route(
    #     "/tutoringCentre/api/get_attendances",
    #     type="json",
    #     auth="public",
    # )
    # def _get_attendances(self, student_id, year, month):
    #     try:
    #         year = int(year)
    #         month = int(month)
    #     except ValueError:
    #         return {"error": "年月格式錯誤"}

    #     today_date = datetime.now().date()
    #     from_date = datetime.strptime(f"{year}-{month:02d}-01", "%Y-%m-%d")
    #     to_date = datetime.strptime(f"{year}-{month:02d}-31", "%Y-%m-%d")

    #     attendances = (
    #         request.env["tutoring_centre.course_attendance_line"]
    #         .sudo()
    #         .search(
    #             [
    #                 ("student_id", "=", student_id),
    #                 ("end_time", "!=", None),
    #                 # ("start_time", "<=", to_date),
    #             ]
    #         )
    #     )
    #     _logger.info(f"attendances------{attendances}")

    #     if not attendances:
    #         return {"error": "未找到指定條件之出席紀錄"}

    #     attendance_records = []
    #     for attendance in attendances:
    #         # if attendance.start_time.start_time.date() != today_date:
    #         attendance_records.append(
    #             {
    #                 "start_time": attendance.start_time,
    #                 "end_time": attendance.end_time,
    #                 "attended": attendance.attended,
    #                 "remark": attendance.remark,
    #             }
    #         )
    #     return attendance_records

# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import base64


class CardHaloTest(http.Controller):
    @http.route(["/halo"], type="json", auth="public", method=["POST"])
    def get_halo(self):
        employees = request.env["hr.employee"].sudo().search([])

        employee_fields = request.env["hr.employee"]._fields.keys()

        employee_data = [
            {field: getattr(employee, field) for field in employee_fields}
            for employee in employees
        ]

        # 取得 ir.attachment 資料
        attachment_data = (
            request.env["ir.attachment"].sudo().search([("id", "=", 1277)])
        )

        # 將 attachment_data 轉換為字典，並添加到 employee_data
        attachment_dict = {
            field: getattr(attachment_data, field)
            for field in attachment_data._fields.keys()
        }
        raw_base64 = base64.b64encode(attachment_dict["raw"]).decode("utf-8")
        employee_data.append({"attachment_data": {"raw_base64": raw_base64}})

        data = {
            "status": 200,
            "response": employee_data,
            "message": "All Employees Returned",
        }
        return data

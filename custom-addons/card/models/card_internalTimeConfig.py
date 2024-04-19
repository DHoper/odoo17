# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions
import logging

_logger = logging.getLogger(__name__)


class CardTimeConfigModel(models.Model):
    _name = "card.internal_time_config"
    _description = "許可時間設置"

    timeConfig_name = fields.Char(string="組態名稱", size=15, required=True)
    timeConfig_brief = fields.Char(string="描述", required=False)

    color = fields.Integer("標籤顏色", default=0)

    @api.depends("timeConfig_name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.timeConfig_name

    def _default_permissions(self, startTime, endTime):
        return [
            {"day_of_week": day, "start_time": startTime, "end_time": endTime}
            for day in [
                "sunday",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ]
        ]

    timeConfig_permissions = fields.One2many(
        "card.internal_time_config.permissions",
        "config_id",
        string="時間權限",
        default=lambda self: self._default_permissions(
            self._context.get("default_start_time", "09"),
            self._context.get("default_end_time", "18"),
        ),
    )

    @api.model
    def create(self, values):
        if "timeConfig_name" in values and not values["timeConfig_name"].startswith(
            "(時間)"
        ):
            values["timeConfig_name"] = "(時間)" + values["timeConfig_name"]
        return super(CardTimeConfigModel, self).create(values)

    def write(self, values):
        if "timeConfig_name" in values and not values["timeConfig_name"].startswith(
            "(時間)"
        ):
            values["timeConfig_name"] = "(時間)" + values["timeConfig_name"]
        return super(CardTimeConfigModel, self).write(values)


class TimePermissions(models.Model):
    _name = "card.internal_time_config.permissions"
    _description = "時間權限"

    day_of_week = fields.Selection(
        [
            ("sunday", "星期日"),
            ("monday", "星期一"),
            ("tuesday", "星期二"),
            ("wednesday", "星期三"),
            ("thursday", "星期四"),
            ("friday", "星期五"),
            ("saturday", "星期六"),
        ],
        string="日期(星期)",
        required=True,
    )
    is_active = fields.Boolean(string="啟用", default=True)

    @api.constrains("day_of_week", "config_id")
    def _check_unique_day_of_week_per_config(self):
        for record in self:
            if record.day_of_week and record.config_id:
                existing_records = self.search(
                    [
                        ("day_of_week", "=", record.day_of_week),
                        ("config_id", "=", record.config_id.id),
                        ("id", "!=", record.id),
                    ]
                )
                if existing_records:
                    raise exceptions.ValidationError("日期(星期)不可重複！")

    _hours = [(f"{i:02d}", f"{i:02d}:00 {'AM' if i < 12 else 'PM'}") for i in range(24)]
    start_time = fields.Selection(_hours, string="開始時間")
    end_time = fields.Selection(
        _hours,
        string="結束時間",
    )

    @api.onchange("is_active")
    def _set_time_null(self):
        if (
            self.is_active is False
        ):  # 若該field有設置default值 則將會僅在介面(視覺)上起作用，資料庫還是會被存入default值
            self.start_time = False
            self.end_time = False

    @api.constrains("end_time", "start_time")
    def _check_end_time(self):
        for record in self:
            if (
                record.end_time
                and record.start_time
                and int(record.end_time) <= int(record.start_time)
            ):
                raise exceptions.ValidationError("時間許可的結束時間必須大於開始時間！")

    config_id = fields.Many2one(
        "card.internal_time_config", string="時間設置", required=True, ondelete="cascade"
    )

# -*- coding: utf-8 -*-
{
    "name": "卡片",
    "summary": """
        卡片管理"
    """,
    "description": """
        卡片管理"
    """,
    "version": "0.1",
    "application": True,
    "category": "門禁 & 安全/",
    "installable": True,
    "depends": ["base", "web", "hr", "device"],
    # 順序是有意義的
    "data": [
        "security/ir.model.access.csv",
        "views/card_internalTimeConfig.xml",
        "views/card_internalPermissions.xml",
        "views/card_internalGroup.xml",
        "views/card_internalManagement.xml",
        "views/menus.xml",
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'card_reader/static/src/**/*',
    #     ],
    # },
    "license": "AGPL-3",
}

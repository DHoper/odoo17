# -*- coding: utf-8 -*-
{
    "name": "裝置",
    "summary": """
        裝置管理系統"
    """,
    "description": """
        裝置管理系統"
    """,
    "version": "0.1",
    "application": True,
    "category": "門禁 & 安全/",
    "installable": True,
    "depends": ["base"],
    # 順序是有意義的
    "data": [
        "security/ir.model.access.csv",
        "views/card_reader.xml",
        "views/menus.xml",
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'card_reader/static/src/**/*',
    #     ],
    # },
    "license": "LGPL-3",
}

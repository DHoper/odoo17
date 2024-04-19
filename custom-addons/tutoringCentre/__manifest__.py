# -*- coding: utf-8 -*-
{
    "name": "補習班",
    "summary": """
        補習班
    """,
    "description": """
        補習班"
    """,
    "author": "FJBC",
    "TutorTalk": "",
    "category": "補習班/",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "web",
        "contacts",
        "website",
        "http_routing",
        "mail",
        "im_livechat",
        "website_livechat",
    ],
    "application": True,
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "views/tutoring_centre_im_livechat.xml",
        "views/tutoring_centre_website_templates.xml",
        # "tutoring_centre_class_group.xml",
        "views/tutoring_centre_student.xml",
        "views/tutoring_centre_member_livechat.xml",
        # "views/tutoring_centre_class_group_attendance.xml",
        "views/tutoring_centre_class_group.xml",
        "views/tutoring_centre_course_attendance.xml",
        "views/tutoring_centre_course_announcement.xml",
        "views/tutoring_centre_course.xml",
        "views/tutoring_centre_teacher.xml",
        "data/mail_template_data.xml",
        "data/mail_templates.xml",
        "views/tutoring_centre_member.xml",
        "views/tutorTalk/tutor_talk_channel.xml",
        "views/tutorTalk/tutor_talk_parent_pick.xml",
        "views/menus.xml",
    ],
    "assets": {
        "tutoringCentre.assets_parentPortal": [
            # bootstrap
            ("include", "web._assets_helpers"),
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            # required for fa icons
            # "web/static/src/libs/fontawesome/css/font-awesome.css",
            # include base files from framework
            ("include", "web._assets_bootstrap"),
            ("include", "web._assets_core"),
            # remove some files that we do not use to create a minimal bundle
            # ("remove", "web/static/src/core/**/*"),
            # ("remove", "web/static/lib/luxon/luxon.js"),
            "web/static/src/libs/pdfjs.js",
            "web/static/src/views/fields/file_handler.*",
            # "web/static/src/core/assets.js",
            # "mail/static/src/discuss/**/common/**/*",
            "bus/static/src/**/*",
            "mail/static/src/**/common/**/*",
            # "web/static/src/core/utils/functions.js",
            # "web/static/src/core/browser/browser.js",
            "tutoringCentre/static/src/**/*",
            (
                "remove",
                "tutoringCentre/static/src/views_controller/**/*",
            ),
            (
                "remove",
                "tutoringCentre/static/src/backend_web/**/*",
            ),
        ],
        "web.assets_backend": [
            "tutoringCentre/static/src/views_controller/**/*",
            "tutoringCentre/static/src/backend_web/**/*",
        ],
    },
    "license": "AGPL-3",
}

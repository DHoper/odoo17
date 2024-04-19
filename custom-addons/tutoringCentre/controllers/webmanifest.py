# -*- coding: utf-8 -*-

import json

from odoo import http
from odoo.http import request
from odoo.tools import ustr, file_open


class TutoringCentreManifest(http.Controller):
    @http.route(
        "/tutoringCentre/manifest.webmanifest",
        type="http",
        auth="public",
        methods=["GET"],
    )
    def webmanifest(self):
        manifest = {
            "name": "TutorTalk",
            "short_name": "TTalk",
            "scope": "/tutoringCentre",
            "start_url": "/tutoringCentre",
            "display": "standalone",
            "background_color": "#34495E",
            "theme_color": "#34495E",
            "prefer_related_applications": False,
        }
        icon_sizes = ["192x192", "512x512"]
        manifest["icons"] = [
            {
                "src": "/tutoringCentre/static/src/img/icon.png",
                "sizes": size,
                "type": "image/png",
            }
            for size in icon_sizes
        ]
        body = json.dumps(manifest, default=ustr)
        response = request.make_response(
            body,
            [
                ("Content-Type", "application/manifest+json"),
            ],
        )
        return response

    @http.route(
        "/tutoringCentre/service-worker",
        type="http",
        auth="public",
        methods=["GET"],
    )
    def service_worker(self):
        response = request.make_response(
            self._get_service_worker_content(),
            [
                ("Content-Type", "text/javascript"),
                ("Service-Worker-Allowed", "/tutoringCentre"),
            ],
        )
        return response

    def _get_service_worker_content(self):
        with file_open("tutoringCentre/static/src/service_worker.js") as f:
            body = f.read()
            return body
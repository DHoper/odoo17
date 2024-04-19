from odoo.http import request, route, Controller
import logging


_logger = logging.getLogger(__name__)


class TutoringCentreBackendWebController(Controller):
    @route(
        "/tutoringCentre/api/backend_web/get_class_group_info",
        type="json",
        auth="public",
    )
    def _get_class_group_info(self, channel_id):
        channel = request.env["discuss.channel"].browse(channel_id)
        if channel:
            class_group = request.env["tutoring_centre.class_group"].search(
                [("announcementChannel", "=", channel.id)], limit=1
            )
        if class_group:
            return class_group.read()[0]
        else:
            return False

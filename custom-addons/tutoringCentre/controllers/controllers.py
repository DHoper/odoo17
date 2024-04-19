from odoo.http import request, route, Controller
from odoo.fields import Command
from odoo.addons.mail.models.discuss.mail_guest import add_guest_to_context
import logging


_logger = logging.getLogger(__name__)


class TutoringCentreClassGroupController(Controller):
    @route(
        "/tutoringCentre/api/userInfo",
        type="json",
        auth="public",
    )
    def _get_user_info(self):
        return request.env.user.read()[0]

    @route(
        "/tutoringCentre/api/get_user_avatar",
        type="json",
        auth="public",
    )
    def _get_user_avatar(self, user_id):
        if not user_id:
            return False
        avatar = request.env["res.users"].sudo().browse(user_id).image_128
        return avatar
    
    @route(
        ["/tutoringCentre", "/tutoringCentre/<path:subpath>"],
        auth="public",
        website=True,
        sitemap=True,
    )
    def _render_tutoringCentre(self, config_id=None):
        return request.render(
            "tutoringCentre.root",
            {
                "session_info": request.env["ir.http"].get_frontend_session_info(),
            },
        )

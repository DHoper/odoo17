/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";

export class TutoringCentreLivechatKanbanController extends KanbanController {
    setup() {
        super.setup(...arguments);
    }

    async openRecord(record) {
        console.log("record.data.is_member", record.data.is_member);
        if (!record.data.is_member) {
            return super.openRecord(record);
        }
        this.actionService.doAction("mail.action_discuss", {
            name: _t("Discuss"),
            additionalContext: { active_id: record.resId },
        });
    }
}

const tutorTalkLivechatKanbanView = {
    ...kanbanView,
    Controller: TutoringCentreLivechatKanbanController,
};

registry
    .category("views")
    .add(
        "tutoringCentre.livechat_kanban",
        tutorTalkLivechatKanbanView
    );

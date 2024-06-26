/* @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";

export class TutoringCentreClassGroupChannelKanbanController extends KanbanController {
    setup() {
        super.setup(...arguments);
    }

    async openRecord(record) {
        // if (!record.data.announcementChannel) {
        //     return super.openRecord(record);
        // }
        console.log("record.data.student._currentIds", record.data.student._currentIds);
        this.actionService.doAction("tutoringCentre.discuss_channel_view_action", {
            additionalContext: { students: record.data.student._currentIds },
        });
    }
}

const TutoringCentreClassGroupChannelKanbanView = {
    ...kanbanView,
    Controller: TutoringCentreClassGroupChannelKanbanController,
};

registry
    .category("views")
    .add(
        "tutoringCentre.course_channel_kanban",
        TutoringCentreClassGroupChannelKanbanView
    );

/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Discuss } from "@mail/core/common/discuss";
import { useService } from "@web/core/utils/hooks";
import { useEffect, useState } from "@odoo/owl";

patch(Discuss.prototype, {
    setup() {
        super.setup(...arguments);
        this.rpc = useService("rpc")
        this.tutoring_centre_state = useState({
            class_group: null,
            open_popup: false
        });

        useEffect(() => {
            (async () => {
                if (this.thread && this.thread.type === "livechat") {
                    this.tutoring_centre_state.class_group = await this.rpc("/tutoringCentre/api/backend_web/get_class_group_info", { "channel_id": this.thread.id })
                }
            })()
        }, () => [this.store.discuss.thread])
    },
    format_time(time) {
        let hour = Math.floor(time);
        let minutes = Math.round((time - hour) * 60);
        let period = 'AM';

        if (hour >= 12) {
            period = 'PM';
            if (hour > 12) {
                hour -= 12;
            }
        }
        if (hour === 0) {
            hour = 12;
        }

        let formatted_hour = hour.toString().padStart(2, '0');
        let formatted_minutes = minutes.toString().padStart(2, '0');

        return `${formatted_hour}:${formatted_minutes} ${period}`;
    }
});

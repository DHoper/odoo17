/* @odoo-module */

import { reactive, useState } from "@odoo/owl";
import { session } from "@web/session";

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
// import { _t } from "@web/core/l10n/translation";

export class TutoringCentreAnnouncement {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.rpc = services.rpc;
        this.messagingService = services["mail.messaging"];
        this.member = services["tutoringCentre_member"];
    }

    async setup() {
        this.class_groups = this.member.memberInfo.student[0].class_groups;
        this.class_groups_ids = [];
        this.announceMessages = {};

        await this._init();
    }

    async _init() {
        for (const class_group of this.class_groups) {
            if (!class_group.announcementChannel) return;
            this.class_groups_ids.push(class_group.id);

            this.busService.addChannel(`${class_group.announcementChannel[0]}`);
            this.busService.subscribe(
                "discuss.channel/new_message",
                payload => {
                    console.log(payload);
                    if (payload.id !== class_group.announcementChannel[0]) return;
                }
            );
        }
    }

    async fetchMessages(ids) {
        for (const id of ids) {
            const { messages } = await this.rpc(
                "/tutoringCentre/api/announcement/fetch_announcement_messages",
                { class_group_id: id }
            );
            this.announceMessages[id] = reactive(messages.reverse());
        }
    }
}

export const tutoringCentreAnnouncement = {
    dependencies: [
        "rpc",
        "bus_service",
        "mail.messaging",
        "tutoringCentre_member",
    ],
    async start(env, services) {
        const tutoringCentreLiveChat = reactive(
            new TutoringCentreAnnouncement(env, services)
        );
        await tutoringCentreLiveChat.setup(env, services);
        return tutoringCentreLiveChat;
    },
};
registry
    .category("services")
    .add("tutoringCentre_announcement", tutoringCentreAnnouncement);

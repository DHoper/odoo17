/* @odoo-module */

import { reactive, useState } from "@odoo/owl";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
// import { _t } from "@web/core/l10n/translation";
export class TutoringCentreMember {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.rpc = services.rpc;
        this.router = services["tutoringCentre_router"];
    }

    async setup() {
        this.user;
        this.memberInfo;
        this.state = reactive({
            registration: false,
        });
        await this._init();
    }

    async _init() {
        this.user = await this.rpc("/tutoringCentre/api/userInfo");
        console.log(this.user, "member");
        if (!this.user || !this.user.active)
            browser.location.assign("/web/login?redirect=/tutoringCentre/");
        this.memberInfo = await this.rpc("/tutoringCentre/api/memberInfo", {
            userID: this.user.id,
        });
        if (!this.memberInfo || !this.memberInfo.is_active) {
            const aa = await this.rpc("/web/session/get_session_info");
            console.log(aa);
            await this.rpc("/web/session/destroy");
            browser.location.assign("/web/login?redirect=/tutoringCentre/");
        }

        //以下暫棄
        if (!this.memberInfo) {
            this.state.registration = false;
            setTimeout(() => {
                this.router.navigate("member_register", { accessible: true }); // 待解決--async問題
            }, 700);
        } else {
            this.memberInfo.portal_user = parseInt(
                this.memberInfo.portal_user
            );

            this.state.registration = true;
        }
    }
}

export const tutoringCentreMember = {
    dependencies: ["rpc", "bus_service", "tutoringCentre_router"],
    async start(env, services) {
        const tutoringCentreMember = reactive(
            new TutoringCentreMember(env, services)
        );
        await tutoringCentreMember.setup(env, services);
        return tutoringCentreMember;
    },
};
registry
    .category("services")
    .add("tutoringCentre_member", tutoringCentreMember);

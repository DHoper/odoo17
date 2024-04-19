/** @odoo-module */
import { Component, onWillStart, useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MemberRegister extends Component {
    static template = "tutoringCentre.Member_register";
    static props = ["accessible"];
    async setup() {
        this.router = useService("tutoringCentre_router");
        this.rpc = useService("rpc");
        // this.memberService = useState(useService("tutoringCentre_member"));
        this.user;
        this.state = useState({
            studentName: "",
            birthDate: null,
            step: 0,
        });

        onWillStart(async () => {
            if (!this.props.accessible) {
                this.router.navigate("default");
            }
            this.router.bottomNav = false;
            this.user = await this.rpc("/tutoringCentre/api/userInfo");
        });
    }

    async submitForm() {
        const im_channels = await this.rpc(
            "/tutoringCentre/api/tutorTalk/livechat/fetch_channels"
        );
        const class_group_ids = [7];
        const channel_ids = [];

        const response = await this.rpc("/tutoringCentre/api/createMember", {
            studentName: this.state.studentName,
            class_group_ids: class_group_ids,
            channel_ids: channel_ids,
        });
        if (response) {
            this.router.navigate("default");
        } else {
            alert("未成功!");
        }
    }
}

/** @odoo-module */
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ChatWindow } from "./ChatWindow/ChatWindow";
export class TutorTalk extends Component {
    static template = "tutorTalk.Root";
    static components = { ChatWindow };
    static props = {};
    async setup() {
        this.rpc = useService("rpc");
        this.router = useService("tutoringCentre_router");
        this.member = useService("tutoringCentre_member");
        this.livechat = useService("tutoringCentre_liveChat");
        this.state = useState({
            live_channels: null,
            announce_channels: null,
            currentChannelInfo: {
                id: null,
                name: "",
                image: "",
            },
            showChatWindow: false,
            animateClass: "",
            last_message_list: null,
        });
        this.openChatWindow = this.openChatWindow.bind(this);
        this.closeChatWindow = this.closeChatWindow.bind(this);

        onWillStart(async () => {
            this.state.live_channels = this.livechat.live_channels;
            this.state.announce_channels = this.livechat.announce_channels;

            this.state.last_message_list = this.livechat.last_message_list;
        });
    }

    openChatWindow(id, name, image) {
        name = name.replace("補習班-", "");
        this.state.currentChannelInfo = { id, name, image };
        this.state.animateClass = "animate__slideInRight";
        this.state.showChatWindow = true;
        this.livechat.new_message_notify[id] = false;
    }

    closeChatWindow() {
        this.state.animateClass = "animate__slideOutRight";
        setTimeout(() => {
            this.state.showChatWindow = false;
        }, 750);
    }
}

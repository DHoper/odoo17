/** @odoo-module */

import { loadJS } from "@web/core/assets";
import { getColor } from "@web/core/colors/colors";
import {
    Component,
    useState,
    useEffect,
    useRef,
    onWillStart,
} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class ChatWindow extends Component {
    static template = "tutorTalk.ChatWindow";
    static props = ["close", "channel_info"];
    setup() {
        this.rpc = useService("rpc");
        this.liveChat = useService("tutoringCentre_liveChat");
        this.userName = _t("Visitor");
        this.member = useState(useService("tutoringCentre_member"));
        this.textarea = useRef("textarea");
        this.state = useState({
            channelMessages: [],
            text: "",
            parentPickLoading: false,
            parentPickShowPop: false,
            parentPickPopText: "",
            in_livechat: false,
            avatar_images: {}
        });
        this.chatListRef = useRef("chatList");

        onWillStart(async () => {
            const id = this.props.channel_info.id;

            if (id in this.liveChat.announce_channel_messages) {
                this.state.in_livechat = false;
                this.state.channelMessages =
                    this.liveChat.announce_channel_messages[id];
                if (this.liveChat.announce_channel_messages[id] && this.liveChat.announce_channel_messages[id].length > 0) {
                    for (const message of this.state.channelMessages) {
                        await this.getMessageAvatar(message.author.user.id)
                    }
                }

            } else {
                this.state.in_livechat = true;
                this.state.channelMessages =
                    this.liveChat.live_channel_messages[id];
                if (this.liveChat.live_channel_messages[id] && (this.liveChat.live_channel_messages[id].length > 0)) {
                    for (const message of this.state.channelMessages) {
                        await this.getMessageAvatar(message.author.user.id)
                    }
                }
            }

            window.history.pushState({ chatWindow: true }, '')

            window.addEventListener('popstate', (event) => {
                // const previousState = event.state;
                this.props.close()
            });
        });

        useEffect(
            () => {
                if (this.state.channelMessages.length > 0) {
                    this.chatListRef.el.scrollTop = this.chatListRef.el.scrollHeight;
                }
            },
            () => [this.state.channelMessages.length]
        );
    }
    autoResize() {
        this.textarea.el.style.height = 0;
        this.textarea.el.style.height = `${Math.min(
            this.textarea.el.scrollHeight,
            100
        )}px`;
    }

    async getMessageAvatar(id) {
        if (this.state.avatar_images.hasOwnProperty(id)) {
            return this.state.avatar_images[id]
        } else {
            const avatar_image = await this.rpc("/tutoringCentre/api/get_user_avatar", { id })
            this.state.avatar_images[id] = avatar_image
            return avatar_image
        }
    }

    async parentPick() {
        this.state.parentPickLoading = true;
        if (this.member.memberInfo.student) {
            for (const student of this.member.memberInfo.student) {
                if (student.active_channels.indexOf(this.props.channel_info.id) !== -1) {
                    const response = await this.rpc(
                        "/tutoringCentre/api/tutorTalk/parentPickup",
                        {
                            childName: student.name,
                        }
                    );
                    if (response) {
                        this.state.parentPickLoading = false;
                        this.state.parentPickPopText = "通知成功，請前往接送小朋友。";
                        document.getElementById("parentPick").showModal();
                    } else {
                        this.state.parentPickLoading = true;
                        this.state.parentPickPopText =
                            "通知失敗，請再嘗試一次，或聯絡客服人員。";
                        document.getElementById("parentPick").showModal();
                    }
                }
            }
        }

    }
    async onClickSendMessage() {
        this.liveChat.sendMessage(this.props.channel_info.id, this.state.text);
        this.state.text = "";
    }
}

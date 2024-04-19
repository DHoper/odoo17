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

export class AnnouncementWindow extends Component {
    static template = "announcement.AnnouncementWindow";
    static props = ["close", "class_group"];
    setup() {
        this.rpc = useService("rpc");
        this.userName = _t("Visitor");
        this.member = useState(useService("tutoringCentre_member"));
        this.announcement = useState(
            useService("tutoringCentre_announcement")
        );
        this.textarea = useRef("textarea");
        this.state = useState({
            announceMessages: [],
            text: "",
            parentPickLoading: false,
            parentPickShowPop: false,
            parentPickPopText: "",
        });

        onWillStart(async () => {
            this.state.announceMessages =
                this.announcement.announceMessages[this.props.class_group.id];
        });

        useEffect(
            () => {
                if (this.state.announceMessages.length > 0) {
                    displayNotification(
                        `你有新訊息!:${this.state.announceMessages[-1]}`
                    );
                }
            },
            () => [this.state.announceMessages.length]
        );
    }

    get sanitizedMessages() {
        if (!this.state.announceMessages) return [];
        return this.state.announceMessages.map(message => ({
            ...message,
            sanitizedBody: message.body.replace(/<[^>]*>/g, ""),
        }));
    }

    autoResize() {
        this.textarea.el.style.height = 0;
        this.textarea.el.style.height = `${Math.min(
            this.textarea.el.scrollHeight,
            100
        )}px`;
    }

    timeFormat(time) {
        const dateObject = new Date(time);

        const datePart = dateObject.toISOString().split("T")[0];
        const timePart = dateObject.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });

        return `${timePart}`;
    }
}

function displayNotification(message) {
    if (Notification.permission === "granted") {
        navigator.serviceWorker
            .getRegistration()
            .then(registration => {
                if (registration) {
                    const options = {
                        body: message,
                        vibrate: [200, 100, 200],
                    };

                    registration.showNotification("新訊息", options);
                }
            })
            .catch(err => {
                console.error("Error getting registration:", err);
            });
    }
}

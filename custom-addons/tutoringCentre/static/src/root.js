/** @odoo-module */
import { Component, onWillStart, onRendered, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Home } from "./Home/Home";
import { MemberRegister } from "./pages/Member_register";
import { TutorTalk } from "./TutorTalk/TutorTalk";
import { Router } from "./router";

export class Root extends Component {
    static template = "tutoringCentre.Root";
    static components = {
        Router,
        Home,
        TutorTalk,
        MemberRegister,
    };
    static props = {};
    async setup() {
        onWillStart(() => {
            this.registerServiceWorker();
        });
        this.rpc = useService("rpc");
        this.router = useState(useService("tutoringCentre_router"));
        this.member = useState(useService("tutoringCentre_member"));

        this.state = useState({
            currentRoute: "default",
        });

        this.navigate = this.navigate.bind(this);
    }

    async registerServiceWorker() {
        // const { public_key } = await this.rpc("/tutoringCentre/api/pwa/get_public_key")
        const public_key = `BLyjMjYZWNzOXieCl8DpSkf2LD0dpCB4wtTFPnJKUyKfV4QCqtrgM_y4NOFQswweAQC-jARrv2nYxujRoknxp8Q`;
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker
                .register("/tutoringCentre/service-worker", {
                    scope: "/tutoringCentre",
                })
                .then(async registration => {
                    if (Notification.permission !== "granted") {
                        Notification.requestPermission();
                    }
                    return await registration.pushManager.getSubscription().then(async (subscription) => {
                        if (!subscription && public_key) {
                            const subscribeOptions = {
                                userVisibleOnly: true,
                                applicationServerKey: urlBase64ToUint8Array(public_key)
                            };
                            const new_subscription = await registration.pushManager.subscribe(subscribeOptions);
                            return new_subscription
                        } else {
                            return subscription;
                        }
                    })
                })
                .then(async (subscription) => {
                    subscription = JSON.parse(JSON.stringify(subscription))
                    console.log(subscription);
                    await this.rpc("/tutoringCentre/api/pwa/post_subscription", { subscription, member_id: this.member.memberInfo.id })
                })
                .catch(error => {
                    console.error("Service worker 註冊失敗，錯誤:", error);
                });
        }
    }


    navigate(route) {
        this.router.navigate(route);
        this.state.currentRoute = route;
    }

}


function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }

    return outputArray;
}

/* @odoo-module */

import { reactive, useState, markup } from "@odoo/owl";
import { session } from "@web/session";

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
// import { _t } from "@web/core/l10n/translation";

export class TutoringCentreLiveChat {
    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.rpc = services.rpc;
        this.messagingService = services["mail.messaging"];
        this.member = services["tutoringCentre_member"];
    }

    async setup() {
        this.live_channel_ids = [];
        this.im_livechat_avatars = null,
            this.announce_channel_ids = [];
        this.live_channels = reactive([]);
        this.announce_channels = reactive([]);
        this.live_channel_messages = {};
        this.announce_channel_messages = {};
        this.last_message_list = reactive({});
        this.new_message_notify = reactive({});
        this.last_read_message_ids = null;
        await this._connectChat();

        window.addEventListener('beforeunload', async (event) => {
            const channel_ids = this.announce_channel_ids.concat(this.live_channel_ids)
            const update_channel_ids = []

            for (const id of channel_ids) {
                if (!this.new_message_notify[id]) {
                    update_channel_ids.push(id)
                }
            }
            await this.rpc("/tutoringCentre/api/tutorTalk/livechat/set_last_read_messages", { "channel_ids": update_channel_ids })
        });

    }

    //需加入頻道在資料庫不存在時的處裡邏輯
    async _connectChat() {
        this.live_channel_ids = [];
        const class_groups = [];
        for (const student of this.member.memberInfo.student) {
            if (student.active_channels.length > 0) {
                this.live_channel_ids.push(...student.active_channels);
            }
            class_groups.push(...student.class_groups);
        }
        const im_livechat_ids = [];
        for (const class_group of class_groups) {
            if (
                class_group.im_livechat_id &&
                !im_livechat_ids.includes(class_group.im_livechat_id[0])
            ) {
                im_livechat_ids.push(class_group.im_livechat_id[0]);
            }
        }

        if (im_livechat_ids.length > 0) {
            this.announce_channel_ids = await this.rpc(
                "/tutoringCentre/api/tutorTalk/livechat/fetch_announce_channel_ids",
                { im_livechat_ids }
            );

            this.im_livechat_avatars = reactive(await this.rpc(
                "/tutoringCentre/api/tutorTalk/livechat/fetch_im_livechat_avatar",
                { im_livechat_ids }
            ));

            await this._fetch_channel();

            const channel_ids = this.announce_channel_ids.concat(this.live_channel_ids)
            this.last_read_message_ids = await this.rpc("/tutoringCentre/api/tutorTalk/livechat/fetch_last_read_messages", { channel_ids })

            for (const id of this.live_channel_ids) {
                this.live_channel_messages[id] = []
            }
            for (const id of this.announce_channel_ids) {
                this.announce_channel_messages[id] = []
            }

            await this._connect_channel(
                this.live_channel_messages,
                this.live_channels,
                this.live_channel_ids
            );

            // await this._connect_channel(
            //     this.announce_channel_messages,
            //     this.announce_channels,
            //     this.announce_channel_ids
            // );

            await this._bus_subscribe(
                channel_ids,
                [this.announce_channel_messages, this.live_channel_messages]
            );
        }
    }

    async _fetch_channel() {
        this.live_channels = await this.rpc(
            "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
            {
                channel_ids: this.live_channel_ids,
            }
        );

        this.announce_channels = await this.rpc(
            "/tutoringCentre/api/tutorTalk/livechat/fetch_channels",
            {
                channel_ids: this.announce_channel_ids,
            }
        );
    }
    async _connect_channel(messages_container, channelList, ids) {
        const sortedChannels = [];
        for (const id of ids) {
            const { messages } = await this.rpc("/discuss/channel/messages", {
                channel_id: id,
            });
            const useable_messages = messages.filter(message => {
                if (message.body) {
                    message.body = markup(message.body);
                    message.write_date = this.timeFormat(message.write_date);
                }

                return message.body && message.message_type !== "notification";
            });
            if (useable_messages.length > 0) {
                if (this.last_read_message_ids && useable_messages[0] && (this.last_read_message_ids[id] && useable_messages[0].id > this.last_read_message_ids[id]) && (useable_messages[0].author.user.id != this.member.memberInfo.portal_user)) {
                    this.new_message_notify[id] = true;
                }
                if (useable_messages[0]) {
                    sortedChannels.push({ id, message_id: useable_messages[0].id });
                }

                const message_list = useable_messages.reverse();
                messages_container[id] = message_list;
                if (message_list.length >= 1) {
                    const last_message = message_list[message_list.length - 1];
                    const tempDiv = document.createElement("div");
                    tempDiv.innerHTML = last_message.body
                    const decodedString = tempDiv.textContent || tempDiv.innerText || "";
                    const modifiedMessage = {
                        ...last_message,
                        body: decodedString
                    };
                    this.last_message_list[id] = modifiedMessage;
                }
            }
        }
        sortedChannels.sort((a, b) => new Date(b.message_id) - new Date(a.message_id));
        sortedChannels.reverse();
        sortedChannels.forEach(channel => {
            const hostingChannelIndex = channelList.findIndex(item => item.id === channel.id);
            if (hostingChannelIndex !== -1) {
                const hostingChannel = channelList.splice(hostingChannelIndex, 1)[0];
                channelList.unshift(hostingChannel);
            }
        });
    }
    async _bus_subscribe(ids, messages_container_list) {
        for (const id of ids) {
            this.busService.addChannel(`${id}`);
        }

        this.busService.subscribe("discuss.channel/new_message", payload => {
            if (!ids.includes(payload.id) || !payload.message.body) return;
            const messages_container = messages_container_list.find(item =>
                Object.keys(item).includes(payload.id.toString())
            );

            if (messages_container) {
                payload.message.body = markup(payload.message.body);
                payload.message.write_date = this.timeFormat(payload.message.write_date);
                messages_container[payload.id].push(payload.message);
                const tempDiv = document.createElement("div");
                tempDiv.innerHTML = payload.message.body
                const decodedString = tempDiv.textContent || tempDiv.innerText || "";
                const modifiedMessage = {
                    ...payload.message,
                    body: decodedString
                };
                this.last_message_list[payload.id] = modifiedMessage;
                if (payload.message.author.user.id != this.member.memberInfo.portal_user) { this.new_message_notify[payload.id] = true; }
                if (typeof payload.id === 'number') {
                    const messageContainer = messages_container_list.find(container => container.hasOwnProperty(payload.id));
                    if (messageContainer) {
                        const channelList = messageContainer === messages_container_list[0] ? this.announce_channels : this.live_channels;
                        const hostingChannelIndex = channelList.findIndex(item => item.id === payload.id);
                        if (hostingChannelIndex !== -1) {
                            const hostingChannel = channelList.splice(hostingChannelIndex, 1)[0];
                            channelList.unshift(hostingChannel);
                        }
                    }
                }
            }
        });
        this.busService.subscribe("mail.record/insert", payload => {
            if (!payload.Message) return;
            const foundMessage = messages_container_list
                .flatMap(obj => Object.values(obj))
                .flat()
                .find(message => message.id === payload.Message.id);

            if (!foundMessage) return;

            if (payload.Message.body === "") {
                // 删除消息
                messages_container_list.forEach(container => {
                    Object.keys(container).forEach(key => {
                        const messageArray = container[key];
                        const indexToRemove = messageArray.findIndex(
                            message => message.id === foundMessage.id
                        );
                        if (indexToRemove !== -1) {
                            messageArray.splice(indexToRemove, 1);
                        }
                    });
                });
            } else {
                // 更新消息内容
                foundMessage.body = markup(payload.Message.body);
            }
        });
    }

    // displayNotification(id, title, message) {
    //     if (Notification.permission === "granted") {
    //         navigator.serviceWorker
    //             .getRegistration()
    //             .then(registration => {
    //                 if (registration) {
    //                     registration.getNotifications().then(notifications => {
    //                         notifications.forEach(notification => {
    //                             if (notification.tag === `message_notification_${id}`) {
    //                                 notification.close();
    //                             }
    //                         });
    //                     });
    //                     const options = {
    //                         body: message,
    //                         badge: '/tutoringCentre/static/src/img/icon.png',
    //                         vibrate: [200, 100, 200],
    //                         timestamp: Date.now(),
    //                         tag: `message_notification_${id}`
    //                     };
    //                     registration.showNotification(title, options);
    //                     // this.rpc("/tutoringCentre/api/pwa/push_notify", { member_id: this.member.memberInfo.id, data: options })
    //                 }
    //             })
    //             .catch(err => {
    //                 console.error("Error getting registration:", err);
    //             });
    //     }
    // }



    // onMessage({ detail: notifications }) {
    //     notifications = notifications.filter(
    //         item => item.payload.channel === this.channel
    //     );
    // }

    async sendMessage(channel_id, text) {
        if (!text) return;
        await this.rpc("/tutoringCentre/api/tutorTalk/livechat/send_message", {
            channel_id,
            message: text,
        });
    }

    timeFormat(time) {
        const dateObject = new Date(time.replace(/-/g, "/"));
        const options = {
            hour: "2-digit",
            minute: "2-digit",
        };
        const timePart = dateObject.toLocaleTimeString([], options);

        return timePart;
    }
}

export const tutoringCentreLiveChat = {
    dependencies: [
        "rpc",
        "bus_service",
        "mail.messaging",
        "tutoringCentre_member",
    ],
    async start(env, services) {
        const tutoringCentreLiveChat = reactive(
            new TutoringCentreLiveChat(env, services)
        );
        await tutoringCentreLiveChat.setup(env, services);
        return tutoringCentreLiveChat;
    },
};
registry
    .category("services")
    .add("tutoringCentre_liveChat", tutoringCentreLiveChat);
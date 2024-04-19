/* eslint-disable no-restricted-globals */
const cacheName = "odoo-sw-cache";

self.addEventListener("install", event => {
    event.waitUntil(caches.open(cacheName).then(cache => cache.addAll(["/"]))); //唯一?
});

const navigateOrFetch = async request => {
    try {
        return await fetch(request);
    } catch (error) {
        if (
            request.method === "GET" &&
            ["Failed to fetch", "Load failed"].includes(error.message)
        ) {
            const cache = await caches.open(cacheName);
            const cachedResponse = await cache.match(request);
            if (cachedResponse) {
                return cachedResponse;
            }
        }
        throw error;
    }
};

self.addEventListener("fetch", event => {
    if (
        (event.request.mode === "navigate" &&
            event.request.destination === "document") ||
        event.request.headers.get("accept").includes("text/html")
    ) {
        event.respondWith(navigateOrFetch(event.request));
    }
});

self.addEventListener("push", function (event) {
    const payload = event.data ? event.data.text() : "no payload";
    let data;
    try {
        data = JSON.parse(payload);
    } catch (error) {
        data = payload;
    }
    event.waitUntil(
        self.registration.showNotification(data.title? data.title : "新訊息", {
            body: data.body ? data.body.replace(/<br\s*\/?>/gi, "\n") : data,
            badge: '/tutoringCentre/static/src/img/icon.png',
            vibrate: [200, 100, 200],
            timestamp: Date.now(),
            tag: data.member_id ? `message_notification_${data.member_id}` : null,
        }),
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    event.waitUntil(
        clients.openWindow('https:odoo.fjbcgroup.com/tutoringCentre')
    );
});

// self.addEventListener('pushsubscriptionchange', function (event) {
//     console.log(event);
//     event.waitUntil(
//         fetch("/tutoringCentre/api/pwa/post_subscription", {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 old_endpoint: event.oldSubscription ? event.oldSubscription : null,
//                 new_endpoint: event.newSubscription ? event.newSubscription : null,
//             })
//         })
//     );
// });


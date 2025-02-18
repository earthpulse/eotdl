import { writable } from "svelte/store";
import retrieveNotifications from "$lib/notifications/retrieveNotifications";
import acceptNotification from "$lib/notifications/acceptNotification";
import dismissNotification from "$lib/notifications/dismissNotification";

const createNotifications = () => {
    const { subscribe, set, update } = writable({
        loading: false,
        error: null,
        data: [],
    });
    return {
        subscribe,
        retrieve: async (token) => {
            set({ loading: true, error: null, data: [] });
            try {
                const data = await retrieveNotifications(token);
                console.log(data);
                set({ loading: false, data, error: null });
            } catch (e) {
                set({ loading: false, error: e.message, data: [] });
            }
        },
        accept: async (id, token) => {
            try {
                await acceptNotification(id, token);
                update((state) => {
                    state.data = state.data.filter((notification) => notification.id !== id);
                    return state;
                });
            } catch (e) {
                console.error(e);
            }
        },
        dismiss: async (id, token) => {
            await dismissNotification(id, token);
            update((state) => {
                state.data = state.data.filter((notification) => notification.id !== id);
                return state;
            });
        },
    };
};

export const notifications = createNotifications();

import retrieveNotifications from "$lib/notifications/retrieveNotifications";
import dismissNotification from "$lib/notifications/dismissNotification";

const createNotifications = () => {
    let loading = $state(false);
    let error = $state(null);
    let data = $state([]);
    return {
        get loading() {
            return loading;
        },
        get error() {
            return error;
        },
        get data() {
            return data;
        },
        retrieve: async (token) => {
            try {
                loading = true;
                const data = await retrieveNotifications(token);
                set({ loading: false, data, error: null });
            } catch (e) {
                set({ loading: false, error: e.message, data: [] });
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

export default createNotifications();

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
                data = await retrieveNotifications(token);
                loading = false;
                error = null;
            } catch (e) {
                loading = false;
                error = e.message;
                data = [];
            }
        },
        dismiss: async (id, token) => {
            await dismissNotification(id, token);
            data = data.filter((notification) => notification.id !== id);
        },
    };
};

export default createNotifications();

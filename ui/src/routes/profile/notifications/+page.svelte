<script>
    import { notifications } from "$stores/notifications";
    import { id_token } from "$stores/auth";

    const dismiss = (id) => {
        notifications.dismiss(id, $id_token);
    };
</script>

<div class="w-full flex flex-col gap-3">
    <h1 class="sm:text-left w-full text-2xl">Notifications</h1>
    {#if $notifications.data.length == 0}
        <p>You have no notifications</p>
    {:else}
        {#each $notifications.data as notification}
            <div class="card bg-base-100 shadow-xl mb-4">
                <div class="card-body">
                    <div class="flex justify-between items-center">
                        <div>
                            {#if notification.type == "dataset_update"}
                                <h2 class="card-title text-lg">
                                    Dataset Update Request
                                </h2>
                                <a
                                    href="/datasets/{notification.payload
                                        .dataset_name}?change={notification
                                        .payload.change_id}"
                                    class="text-blue-500 hover:underline"
                                    >See changes</a
                                >
                            {:else if notification.type == "model_update"}
                                <h2 class="card-title text-lg">
                                    Model Update Request
                                </h2>
                                <a
                                    href="/models/{notification.payload
                                        .model_name}?change={notification
                                        .payload.change_id}"
                                    class="text-blue-500 hover:underline"
                                    >See changes</a
                                >
                            {:else if notification.type == "dataset_update_request_declined"}
                                <h2 class="card-title text-lg">
                                    Dataset Update Request Declined
                                </h2>
                                <p>
                                    {notification.payload.message}
                                </p>
                            {:else if notification.type == "model_update_request_declined"}
                                <h2 class="card-title text-lg">
                                    Model Update Request Declined
                                </h2>
                                <p>
                                    {notification.payload.message}
                                </p>
                            {:else if notification.type == "dataset_update_request_accepted"}
                                <h2 class="card-title text-lg">
                                    Dataset Update Request Accepted
                                </h2>
                                <p>
                                    {notification.payload.message}
                                </p>
                            {:else if notification.type == "model_update_request_accepted"}
                                <h2 class="card-title text-lg">
                                    Model Update Request Accepted
                                </h2>
                                <p>
                                    {notification.payload.message}
                                </p>
                            {:else}
                                <h2 class="card-title text-lg text-error">
                                    Invalid Notification Type
                                </h2>
                            {/if}
                            <p class="text-sm text-gray-500">
                                Received on {notification.createdAt}
                            </p>
                        </div>
                        <div class="card-actions">
                            <button
                                class="btn btn-sm btn-outline btn-error"
                                on:click={() => dismiss(notification.id)}
                            >
                                Dismiss</button
                            >
                        </div>
                    </div>
                </div>
            </div>
        {/each}
    {/if}
</div>

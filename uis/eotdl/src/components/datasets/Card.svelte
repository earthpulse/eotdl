<script>
    import { parseISO, formatDistanceToNow } from "date-fns";
    import HeartOutline from "svelte-material-icons/HeartOutline.svelte";

    export let dataset;
    export let liked;
</script>

<a
    href="/datasets/{dataset.name}"
    class="w-full bg-gray-100 border-2 rounded-xl p-3 flex flex-col justify-between h-[150px]"
>
    <span
        ><p>{dataset.name}</p>
        <p class="text-gray-400">{dataset.description}</p></span
    >
    <span>
        <div class="flex flex-wrap gap-1 content-start">
            {#each dataset.tags as tag}
                <p class="badge badge-outline">{tag}</p>
            {/each}
        </div>
        <span class="flex flex-row w-full justify-between text-gray-400">
            <p>
                Created {formatDistanceToNow(parseISO(dataset.createdAt))} ago
            </p>
            <span class="flex flex-row items-center">
                <HeartOutline color={liked ? "red" : "gray"} />
                <p>{dataset.likes}</p>
            </span>
        </span>
    </span>
</a>

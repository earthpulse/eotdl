<script>
    import { parseISO, formatDistanceToNow } from "date-fns";
    import HeartOutline from "svelte-material-icons/HeartOutline.svelte";

    export let dataset;
    export let liked = null;
</script>

<a
    href="/datasets/{dataset.name}"
    class="w-full bg-gray-100 border-2 rounded-xl p-3 flex flex-col justify-between h-full text-left"
>
    <span
        ><p class="font-bold">{dataset.name}</p>
        <p class="text-gray-400">{dataset.description}</p></span
    >
    <span>
        <div class="flex flex-wrap gap-1 content-start mt-1">
            {#each dataset.tags as tag}
                <p
                    class="badge badge-outline bg-white border-slate-300 text-slate-400 text-xs h-full"
                >
                    {tag}
                </p>
            {/each}
        </div>
        <span
            class="flex flex-row w-full justify-between text-gray-400 text-xs mt-1"
        >
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

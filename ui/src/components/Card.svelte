<script>
    import { parseISO, formatDistanceToNow } from "date-fns";
    import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
    import Download from "svelte-material-icons/CloudDownloadOutline.svelte";
    import Sd from "svelte-material-icons/Sd.svelte";
    import CheckDecagramOutline from "svelte-material-icons/CheckDecagramOutline.svelte";
    import formatFileSize from "$lib/datasets/formatFileSize.js";

    export let data;
    export let liked = null;
    export let link = "datasets";
</script>

<a
    href="/{link}/{data.name}"
    class="w-full bg-gray-100 border-2 rounded-xl p-3 flex flex-col justify-between h-full text-left"
>
    <span>
        <p class="font-bold">{data.name}</p>
    </span>
    <span>
        <div class="flex flex-wrap gap-1 content-start mt-1">
            {#each data.tags as tag}
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
                Created {formatDistanceToNow(parseISO(data.createdAt))} ago
            </p>
            <span class="flex flex-row gap-2 items-center">
                <span class="flex flex-row items-center gap-1">
                    <HeartOutline color={liked ? "red" : "gray"} />
                    <p>{data.likes}</p>
                </span>
                <!-- <span class="flex flex-row items-center gap-1">
                    <Download color="gray" size={14} />
                    <p>{data.downloads}</p>
                </span> -->
                <span class="flex flex-row items-center gap-1">
                    <Sd color="gray" size={14} />
                    <p>
                        {formatFileSize(
                            data.versions[data.versions.length - 1]?.size || 0
                        )}
                    </p>
                </span>
                <span class="flex flex-row items-center gap-1">
                    <CheckDecagramOutline color="gray" size={14} />
                    <p>Q{data.quality}</p>
                </span>
            </span>
        </span>
    </span>
</a>

<script>
    export let dataset;
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
        <p class="text-gray-400">{dataset.createdAt}</p>
    </span>
</a>

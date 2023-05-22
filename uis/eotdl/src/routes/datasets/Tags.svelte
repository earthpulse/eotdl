<script>
    export let tags = [];
    export let selected_tags = [];

    const toggleTag = (tag) => {
        if (selected_tags.includes(tag)) {
            selected_tags = selected_tags.filter((t) => t !== tag);
        } else {
            selected_tags = [...selected_tags, tag];
        }
    };
</script>

<div class="flex flex-wrap gap-1 content-start">
    {#each tags as tag}
        <button
            class="badge badge-outline bg-white text-slate-400 text-xs {selected_tags.includes(
                tag
            ) && 'badge-accent'}"
            on:click={() => toggleTag(tag)}
        >
            {tag}
        </button>
    {/each}
</div>

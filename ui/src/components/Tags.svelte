<script>
    export let tags = [];
    export let selected_tags = [];
    export let onToggleTag = () => {};

    const toggleTag = (tag) => {
        if (selected_tags.includes(tag)) {
            selected_tags = selected_tags.filter((t) => t !== tag);
        } else {
            selected_tags = [...selected_tags, tag];
        }
        onToggleTag(selected_tags);
    };
</script>

<div class="flex flex-wrap gap-1 content-start">
    {#each tags as tag}
        <button
            class="badge text-slate-400 text-xs {selected_tags.includes(
                tag
            ) ? 'badge badge-accent bg-green-100 text-slate-600 ' : 'badge-outline'}"
            on:click={() => toggleTag(tag)}
        >
            {tag}
        </button>
    {/each}
</div>

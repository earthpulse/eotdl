<script>
    export let tags = [];
    export let selected_tags = [];
    export let onToggleTag = () => {};

    let categories = [];

    const toggleTag = (tag) => {
        if (selected_tags.includes(tag)) {
            selected_tags = selected_tags.filter((t) => t !== tag);
        } else {
            selected_tags = [...selected_tags, tag];
        }
        onToggleTag(selected_tags);
    };

    tags.forEach((tag) => {
        if (!categories.includes(tag.category)) {
            categories.push(tag.category);
        }
    });
</script>

<div class="flex flex-row flex-wrap gap-2 content-start justify-center">
    {#each categories as category}
        <div class="w-full gap-2 flex flex-row items-center flex-wrap">
            <h1 class="text-slate-500 text-xs">
                {category.charAt(0).toUpperCase() + category.slice(1)}:
            </h1>
            {#each tags as tag}
                {#if tag.category == category}
                    <button
                        class={`badge text-slate-400 border-slate-300 text-xs mx-[1px] hover:scale-105 transition-all duration-200 cursor-pointer ${
                            selected_tags.includes(tag.name)
                                ? `badge badge-outline text-white border-0`
                                : "badge-outline"
                        }`}
                        style={`${selected_tags.includes(tag.name) && `background-color: ${tag.color};`}`}
                        on:click={() => toggleTag(tag.name)}
                    >
                        {tag.name}
                    </button>
                {/if}
            {/each}
        </div>
    {/each}
</div>

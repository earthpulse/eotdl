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

    tags.forEach(tag => {
        console.log(tag.category);
        if(!categories.includes(tag.category)){
            categories.push(tag.category);
        }
    })
    console.log(categories);
</script>

<div class="flex flex-row flex-wrap gap-2 content-start justify-center">
    {#each categories as category}    
        <div class="w-full gap-2">
            <h1 class="font-bold">{category.charAt(0).toUpperCase() + category.slice(1)}</h1>
            {#each tags as tag}
                {#if tag.category == category}                
                <button
                    class="badge text-slate-400 text-xs mx-[2px] {selected_tags.includes(
                        tag
                    ) ? 'badge badge-accent bg-green-100 text-slate-600 ' : 'badge-outline'}"
                    on:click={() => toggleTag(tag)}
                >
                    {tag.name}
                </button>
                {/if}
            {/each}
        </div>
    {/each}
</div>

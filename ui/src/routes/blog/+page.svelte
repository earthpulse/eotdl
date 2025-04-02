<script>
    import Card from "./Card.svelte";
    import HeartOutline from "svelte-material-icons/HeartOutline.svelte";

    export let data;

    let selected_tags = [];
    const toggleTag = (tag) => {
        if (selected_tags.includes(tag)) {
            selected_tags = selected_tags.filter((t) => t !== tag);
        } else {
            selected_tags = [...selected_tags, tag];
        }
    };

    let filterName = "";
    let show_liked = false;
    let filtered_posts;
    $: {
        filtered_posts = data.posts
            ?.filter((post) => {
                if (selected_tags.length === 0) return true;
                return selected_tags.every((tag) => post.tags.includes(tag));
            })
            .filter((post) => {
                if (filterName.length === 0) return true;
                return (post.title + post.description)
                    .toLowerCase()
                    .includes(filterName.toLowerCase());
            });
        if (show_liked) {
            filtered_posts = filtered_posts.filter((post) =>
                data.liked_posts.includes(post.slug),
            );
        }
    }

    const maxVisiblePosts = 5;
    let currentPage = 0;
    $: numPages = Math.ceil(filtered_posts?.length / maxVisiblePosts);
    $: if (numPages > 0) currentPage = 0;
    $: visible_posts = filtered_posts?.slice(
        currentPage * maxVisiblePosts,
        (currentPage + 1) * maxVisiblePosts,
    );
</script>

<svelte:head>
    <title>EOTDL | Blog</title>
    <meta name="description" content="This is the EOTDL blog." />
</svelte:head>

<div class="w-full flex flex-col items-center">
    <div
        class="px-3 py-10 mt-10 gap-3 w-full max-w-4xl flex flex-col items-center"
    >
        <div class="grid grid-cols-1 sm:grid-cols-[auto_auto] gap-8 w-full">
            <div class="flex flex-col">
                <div class="flex flew-row justify-between text-3xl">
                    <h1 class="font-bold mb-3">Blog</h1>
                    <p class="text-gray-400">{filtered_posts?.length || 0}</p>
                </div>
                <input
                    class="input input-bordered w-full max-w-full input-xs"
                    type="text"
                    placeholder="Filter by name"
                    bind:value={filterName}
                />
            </div>

            <div class="flex flex-wrap gap-1 content-start">
                {#each data?.tags as tag}
                    <button
                        class="cursor-pointer border-slate-300 badge badge-outline text-slate-400 text-xs transition-all duration-200 hover:scale-105 {selected_tags.includes(
                            tag,
                        ) &&
                            'badge badge-outline bg-[rgb(74,191,167)] text-slate-600'}"
                        on:click={() => toggleTag(tag)}
                    >
                        {tag}
                    </button>
                {/each}
            </div>
        </div>
        <a
            class="self-start text-green-200 hover:underline"
            href="https://github.com/earthpulse/eotdl/tree/main/tutorials/notebooks"
            target="_blank">Open on GitHub</a
        >
        <div class="flex flex-col gap-3 w-full max-w-6xl">
            {#if visible_posts?.length > 0}
                {#each visible_posts as post}
                    <Card {post} />
                {/each}
            {/if}
        </div>
        <div>
            {#if numPages > 1}
                <div class="btn-group grid grid-cols-2 w-[200px] btn-xs mt-3">
                    <button
                        class="btn btn-outline btn-xs"
                        disabled={currentPage === 0}
                        on:click={() =>
                            (currentPage = Math.max(0, currentPage - 1))}
                        >Previous</button
                    >
                    <button
                        class="btn btn-outline btn-xs"
                        disabled={currentPage === numPages - 1}
                        on:click={() =>
                            (currentPage = Math.min(currentPage + 1, numPages))}
                        >Next</button
                    >
                </div>
            {/if}
        </div>
    </div>
</div>

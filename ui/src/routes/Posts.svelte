<script>
    import Card from "./blog/Card.svelte";
    export let posts;
</script>

<div class="flex flex-col items-center w-full py-[100px] bg-slate-50">
    <div class="gap-3 w-full max-w-4xl text-center flex flex-col px-4">
        <h1 class="text-xl text-left">Recent posts</h1>
        <div class="flex flex-row gap-3 w-full mt-3 p-4">
            {#if posts.length > 0}
                {#each posts as post}
                    <Card {post} />
                {/each}
            {/if}
        </div>
        <a href="/blog" class="self-end mr-6 hover:underline text-green-200"
            >See all</a
        >
    </div>
</div>

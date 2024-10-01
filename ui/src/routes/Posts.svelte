<script>
    import Card from "./blog/Card.svelte";
    export let posts;
</script>

<div
    class="flex flex-col items-center w-full sm:py-[100px] py-[20px] bg-gradient-to-tl from-gray-100 to-white"
>
    <div class="gap-3 w-full max-w-6xl text-center flex flex-col px-4">
        <h1 class="text-xl text-left font-bold">Recent posts</h1>
        <div class="flex flex-col sm:flex-row gap-3 w-full mt-3">
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

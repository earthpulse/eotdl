<script>
    import Card from "$components/Card.svelte";
    import Skeleton from "$components/Skeleton.svelte";

    let { data, title, tags } = $props();
</script>

<div class="flex flex-col items-center w-full pt-10">
    <div class="gap-3 w-full max-w-6xl text-center flex flex-col px-4">
        <h1 class="text-xl text-left font-bold">{title}</h1>
        <div
            class="grid grid-cols-1 sm:grid-cols-3 grid-rows-3 sm:grid-rows-1 gap-3 w-full mt-3"
        >
            {#if data}
                {#each data as item, i}
                    {#if title.includes("models")}
                        <Card data={item} {tags} link="models" />
                    {:else}
                        <Card data={item} {tags} />
                    {/if}
                {/each}
            {:else}
                {#each [1, 2, 3] as _}
                    <Skeleton />
                {/each}
            {/if}
        </div>
    </div>
</div>

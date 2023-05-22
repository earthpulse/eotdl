<script>
    import Card from "./datasets/Card.svelte";
    import Skeleton from "./datasets/Skeleton.svelte";
    export let datasets;
</script>

<div class="flex flex-col items-center w-full">
    <div class="gap-3 w-full max-w-6xl text-center flex flex-col px-4">
        <h1 class="text-xl text-left">Recent Datasets</h1>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
            {#if datasets?.length > 0}
                {#each datasets as dataset}
                    <Card {dataset} />
                {/each}
            {:else}
                {#each [1, 2, 3] as _}
                    <Skeleton />
                {/each}
            {/if}
        </div>
    </div>
</div>

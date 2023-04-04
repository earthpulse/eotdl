<script>
    import Card from "./datasets/Card.svelte";
    export let data;
</script>

<div class="flex flex-col items-center w-full pt-10">
    <div class="gap-3 w-full max-w-6xl text-center flex flex-col px-4">
        <h1 class="text-xl text-left">Popular Datasets</h1>
        <div class="grid grid-cols-3 gap-3 w-full mt-3">
            {#if data?.popular_datasets?.length > 0}
                {#each data?.popular_datasets as dataset}
                    <Card {dataset} />
                {/each}
            {/if}
        </div>
    </div>
</div>

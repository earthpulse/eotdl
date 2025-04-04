<script>
    import Card from "$components/Card.svelte";
    import Skeleton from "$components/Skeleton.svelte";

    let { data, title, tags } = $props();
</script>

<div class="flex flex-col items-center w-full">
    <div class="gap-3 w-full max-w-6xl text-center flex flex-col px-4">
        {#if title.includes("datasets")}
            <h1
                class="font-bold text-3xl w-full text-left pb-6 text-[rgb(74,191,167)]"
            >
                DATASETS
            </h1>
        {:else if title.includes("models")}
            <h1
                class="font-bold text-3xl w-full text-left pb-6 text-[rgb(74,191,167)]"
            >
                MODELS
            </h1>
        {/if}
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

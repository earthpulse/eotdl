<script>
    export let text;
    export let edit = false;
</script>

{#if edit}
    <input class="input input-bordered w-full" type="text" bind:value={text} />
{:else}
    <h1 class="text-4xl">{text}</h1>
{/if}

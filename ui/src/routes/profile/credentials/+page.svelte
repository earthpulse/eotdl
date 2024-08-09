<script>
    import Credentials from "../Credentials.svelte";

    export let data;
</script>

<div class="w-full flex flex-col gap-3">
    <h1 class="sm:text-left w-full text-2xl">Credentials</h1>
    <Credentials {data} />
</div>

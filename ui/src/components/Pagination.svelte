<script>
    export let numPages = 0;
    export let currentPage = 0;
</script>

<div>
    {#if numPages > 1}
        <div class="grid grid-cols-3 w-[250px] btn-xs items-center">
            <button
                class="btn btn-ghost btn-xs disabled:bg-white"
                disabled={currentPage === 0}
                on:click={() => (currentPage = Math.max(0, currentPage - 1))}
                >Previous</button
            >
            <p class="w-full text-center">
                {currentPage + 1} / {numPages}
            </p>
            <button
                class="btn btn-ghost btn-xs disabled:bg-white"
                disabled={currentPage === numPages - 1}
                on:click={() =>
                    (currentPage = Math.min(currentPage + 1, numPages))}
                >Next</button
            >
        </div>
    {/if}
</div>

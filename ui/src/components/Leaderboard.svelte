<script>
    let {
        leaderboard,
        field = "datasets",
        msgText = "Ingest datasets into EOTDL and climb up the leaderboard!",
        textOnLeft = false,
        textOnRight = false,
    } = $props();

    $effect(() => {
        leaderboard = leaderboard?.filter((l) => l[field] > 0);
    });
</script>

<div class="w-full grid place-items-center">
    <div
        class="w-full overflow-x-auto py-10 px-5 flex sm:flex-row flex-col justify-center"
    >
        <h2 class="text-2xl font-bold text-[rgb(74,191,167)] pb-6 sm:hidden">
            Top contributors
        </h2>
        {#if textOnLeft}
            <div class="sm:flex-col sm:w-96 w-500px] hidden sm:flex">
                <h2 class="text-2xl font-bold text-[rgb(74,191,167)] pb-6">
                    Top contributors
                </h2>
                <p>{msgText}</p>
            </div>
        {/if}
        <table class="w-full sm:max-w-2xl max-h-64 max-w">
            <thead>
                <tr class="bg-[rgb(0,50,71)] text-white h-12">
                    <th class="px-4"></th>
                    <th class="text-left px-4">Name</th>
                    <th class="px-4">{field}</th>
                </tr>
            </thead>
            <tbody>
                {#if leaderboard?.length > 0}
                    {#each leaderboard as user, i}
                        <tr
                            class={i % 2
                                ? "active bg-[rgb(74,191,167)] h-12 text-white"
                                : "bg-white h-12"}
                        >
                            <th class="px-4">{i + 1}</th>
                            <td
                                ><p class="sm:w-[400px] w-[225px] px-4">
                                    {user.name}
                                </p></td
                            >
                            <td class="text-center">{user[field]}</td>
                        </tr>
                    {/each}
                {:else}
                    {#each [1, 2, 3, 4, 5] as _, i}
                        <tr class={i % 2 && "active"}>
                            <th>{i + 1}</th>
                            <td
                                ><div
                                    class="animate-pulse bg-slate-100 p-3 rounded-xl w-[200px]"
                                ></div></td
                            >
                            <td
                                ><div
                                    class="animate-pulse bg-slate-100 p-3 rounded-xl w-6"
                                ></div></td
                            >
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
        {#if textOnRight}
            <div class="sm:pl-8 sm:flex-col sm:w-96 w-500px] hidden sm:flex">
                <h2 class="text-2xl font-bold text-[rgb(0,50,71)] pb-6">
                    Top contributors
                </h2>
                <p>{msgText}</p>
            </div>
        {/if}
    </div>
</div>

<script>
    export let leaderboard;
    export let field = "datasets";

    $: console.log(leaderboard);
</script>

<div class="w-full bg-gray-200 grid place-items-center">
    <div class="w-full max-w-2xl overflow-x-auto py-10 px-5">
        <h2 class="text-2xl mb-8">Top contributors</h2>
        <table class="table w-full mt-3">
            <thead>
                <tr>
                    <th />
                    <th>Name</th>
                    <th>{field}</th>
                </tr>
            </thead>
            <tbody>
                {#if leaderboard?.length > 0}
                    {#each leaderboard as user, i}
                        <tr class={i % 2 && "active"}>
                            <th>{i + 1}</th>
                            <td><p class="w-[200px]">{user.name}</p></td>
                            <td>{user[field]}</td>
                        </tr>
                    {/each}
                {:else}
                    {#each [1, 2, 3, 4, 5] as _, i}
                        <tr class={i % 2 && "active"}>
                            <th>{i + 1}</th>
                            <td
                                ><div
                                    class="animate-pulse bg-slate-100 p-3 rounded-xl w-[200px]"
                                /></td
                            >
                            <td
                                ><div
                                    class="animate-pulse bg-slate-100 p-3 rounded-xl w-6"
                                /></td
                            >
                        </tr>
                    {/each}
                {/if}
            </tbody>
        </table>
    </div>
</div>

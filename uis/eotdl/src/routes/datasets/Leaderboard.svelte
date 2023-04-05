<script>
    export let leaderboard;
</script>

<div class="w-full bg-gray-200 grid place-items-center">
    <div class="w-full max-w-2xl overflow-x-auto py-10 px-5">
        <h2 class="text-2xl mb-8">Top contributors</h2>
        <table class="table w-full mt-3">
            <thead>
                <tr>
                    <th />
                    <th>Name</th>
                    <th>Datasets</th>
                </tr>
            </thead>
            <tbody>
                {#each leaderboard as user, i}
                    <tr class={i % 2 && "active"}>
                        <th>{i + 1}</th>
                        <td>{user.name}</td>
                        <td>{user.datasets}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>

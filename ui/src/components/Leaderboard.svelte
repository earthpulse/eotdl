<script>
    import { stringify } from "postcss";

    export let leaderboard;
    export let field = "datasets";
    export let textOnLeft = false;
    export let textOnRight = false;
    $: leaderboard = leaderboard?.filter((l) => l[field] > 0);
</script>

<div class="w-full bg-gray-200 grid place-items-center">
    <div class="w-full overflow-x-auto py-10 px-5 sm:flex justify-center">
        {#if textOnLeft}        
            <div class="p-10 flex flex-col sm:w-96 w-500px]">
                <h2 class="text-2xl font-bold text-[rgb(74,191,167)] pb-6">Top contributors</h2>
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Est dolor, asperiores repellendus quod id cupiditate consequatur tenetur corporis nesciunt. Commodi dignissimos repellendus laudantium quasi nesciunt porro corporis quidem rerum assumenda.</p>
            </div>
        {/if}
        <table class="w-full max-w-2xl max-h-64">
            <thead>
                <tr class="bg-[rgb(77,198,169)] text-green-100 h-14">
                    <th class="px-4"/>
                    <th class="text-left px-4">Name</th>
                    <th class="px-4">{field}</th>
                </tr>
            </thead>
            <tbody>
                {#if leaderboard?.length > 0}
                    {#each leaderboard as user, i}
                        <tr class={i % 2 ? "active bg-slate-200 h-12 bg-opacity-85" : "bg-slate-300 h-12 bg-opacity-70"}>
                            <th class="px-4">{i + 1}</th>
                            <td><p class="w-[400px] px-4">{user.name}</p></td>
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
        {#if textOnRight}        
            <div class="p-10 flex flex-col sm:w-96 w-500px]">
                <h2 class="text-2xl font-bold text-[rgb(74,191,167)] pb-6">Top contributors</h2>
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Est dolor, asperiores repellendus quod id cupiditate consequatur tenetur corporis nesciunt. Commodi dignissimos repellendus laudantium quasi nesciunt porro corporis quidem rerum assumenda.</p>
            </div>
        {/if}
    </div>
</div>

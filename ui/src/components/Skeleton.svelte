<div
    class="w-full bg-gray-100 border-1 border-gray-200 rounded-xl p-3 flex flex-col justify-between h-[100px] text-left"
>
    <span
        ><p class="bg-slate-200 animate-pulse w-20 h-4 rounded-2xl"></p>
        <span>
            <div class="flex flex-wrap gap-1 content-start mt-1">
                {#each [1, 2, 3] as _}
                    <p
                        class="bg-slate-200 animate-pulse w-20 h-4 rounded-2xl"
                    ></p>
                {/each}
            </div>
            <span
                class="flex flex-row w-full justify-between text-gray-400 text-xs mt-1"
            >
                <p
                    class="bg-slate-200 animate-pulse w-[200px] h-4 rounded-2xl"
                ></p>
                <p class="bg-slate-200 animate-pulse w-20 h-4 rounded-2xl"></p>
            </span>
        </span>
    </span>
</div>

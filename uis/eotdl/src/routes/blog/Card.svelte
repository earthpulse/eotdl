<script>
    import { parseISO, format } from "date-fns";

    export let post;
</script>

<a
    href="/blog/{post.slug}"
    class="w-full bg-gray-100 border-2 rounded-xl p-3 flex flex-col justify-between h-[150px] text-left"
>
    <span
        ><p class="font-bold">{post.title}</p>
        <p class="text-gray-400">{post.description}</p></span
    >
    <span>
        <div class="flex flex-wrap gap-1 content-start">
            {#each post.tags as tag}
                <p
                    class="badge badge-outline bg-white border-slate-300 text-slate-400 text-xs"
                >
                    {tag}
                </p>
            {/each}
        </div>
        <span
            class="flex flex-row w-full justify-between text-gray-400 text-xs mt-2"
        >
            <p>
                Published on {format(parseISO(post.date), "MMMM d, yyyy")}
            </p>
        </span>
    </span>
</a>

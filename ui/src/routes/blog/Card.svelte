<script>
    import { parseISO, format } from "date-fns";

    let { post } = $props();
</script>

<a
    href="/blog/{post.slug}"
    class="w-full bg-white rounded-xl p-6 flex flex-col h-full text-left min-h-[210px] gap-3 transition-transform duration-200 hover:scale-105 border-1 border-gray-200"
>
    <div>
        <span>
            <div class="flex flex-wrap gap-1 content-start mt-1">
                {#each post.tags as tag}
                    <p
                        class="badge badge-outline bg-[rgb(74,191,167)] text-slate-600 text-xs"
                    >
                        {tag}
                    </p>
                {/each}
            </div>
        </span>
        <span
            class="flex flex-row w-full justify-between text-gray-400 text-xs mt-2"
        >
            <p>
                Published on {format(parseISO(post.date), "MMMM d, yyyy")}
            </p>
        </span>
    </div>
    <span
        ><p class="font-bold">{post.title}</p>
        <p class="text-gray-400">{post.description}</p></span
    >
</a>

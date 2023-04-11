<script>
    import "../../../styles/post.css";
    import "../../../styles/prism.css";

    export let data;
    const { post } = data;
</script>

<article class="w-full flex flex-col items-center">
    <div class="px-3 py-10 mt-10 w-full max-w-3xl flex flex-col gap-4">
        <div
            class="flex flex-row w-full justify-between text-green-200  text-md"
        >
            <p class="capitalize ">{post.meta.printDate}</p>
            <p>~ {post.meta.printReadingTime} MIN</p>
        </div>
        <div>
            <h1 class="text-left text-2xl font-bold">{post.meta.title}</h1>
            <div class="flex flex-wrap gap-2 max-w-6xl justify-start mt-1">
                {#each post.meta.tags as tag}
                    <p
                        class="badge badge-outline bg-white border-slate-300 text-slate-400 text-xs"
                    >
                        {tag}
                    </p>
                {/each}
            </div>
        </div>
        <span class="w-full flex flex-row justify-between">
            <a href="/blog" class="text-green-200 hover:underline">
                {"<"} Blog</a
            >
        </span>
        <div
            class="post text-left flex flex-col items-center gap-2 pt-3 text-justify"
        >
            {@html post.content}
        </div>
        <span class="w-full flex flex-row justify-between mt-3">
            <a href="/blog" class="text-green-200 hover:underline">
                {"<"} Blog</a
            >
        </span>
    </div>
</article>

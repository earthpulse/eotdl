<script>
  import { parseISO, formatDistanceToNow } from "date-fns";
  import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
  import Sd from "svelte-material-icons/Sd.svelte";
  // import CheckDecagramOutline from "svelte-material-icons/CheckDecagramOutline.svelte";
  import formatFileSize from "$lib/datasets/formatFileSize.js";

  export let data;
  export let liked = null;
  export let link = "datasets";
  export let tags;
  export let img;
</script>

<a
  href="/{link}/{data.name}"
  class="w-full bg-gray-100 border-2 rounded-xl flex flex-col justify-between h-full text-left shadow-xl"
>
  <span>
    <img
      src={data.metadata.thumbnail ? data.metadata.thumbnail : `${img}`}
      class="h-48 rounded-t-lg w-full object-cover"
      alt=""
    />
    <div class="p-3">
      <p class="font-bold">{data.name}</p>
      <p class="text-gray-400 text-xs">
        Created {formatDistanceToNow(parseISO(data.createdAt))} ago
      </p>
    </div>
  </span>
  <span class="p-3">
    <div class="flex flex-wrap gap-1 content-start mt-1 min-h-[20px]">
      {#each data.tags as tag}
        <p
          class="badge border-0 text-slate-100 text-xs"
          style="background-color: {tags?.find((t) => t.name == tag).color ||
            'none'};"
        >
          {tag}
        </p>
      {/each}
    </div>
    <span class="flex flex-col w-full text-gray-400 text-xs mt-1">
      <span class="flex flex-row gap-2 items-center">
        <span class="flex flex-row items-center gap-1">
          <HeartOutline color={liked ? "red" : "gray"} />
          <p>{data.likes}</p>
        </span>
        <!-- <span class="flex flex-row items-center gap-1">
                    <Download color="gray" size={14} />
                    <p>{data.downloads}</p>
                </span> -->
        <span class="flex flex-row items-center gap-1">
          <Sd color="gray" size={14} />
          <p>
            {formatFileSize(data.versions[data.versions.length - 1]?.size || 0)}
          </p>
        </span>
        <!-- <span class="flex flex-row items-center gap-1">
          <CheckDecagramOutline color="gray" size={14} />
          <p>Q{data.quality}</p>
        </span> -->
      </span>
    </span>
  </span>
</a>

<script>
  import Code from "../docs/components/Code.svelte";
  import CLI from "../docs/components/CLI.svelte";
  import TextEditor from "./TextEditor.svelte";
  // import formatFileSize from "../../lib/datasets/formatFileSize.js";

  export let tags;
  export let submit;
  export let text;
  export let forCreate = false;
  export let required = false;
  export let current_tags = [];
  export let name;
  export let authors;
  export let source;
  export let license;
  export let content;
  export let quality = 0;
  let files;
  let loading = false;
  let error = null;
  $: selected_tags = current_tags;

  const ingest = async () => {
    error = null;
    if (source && !validate_source(source)) return;
    loading = true;
    try {
      if (authors instanceof Array) authors = authors.join(",");
      if (forCreate) {
        if (!validateModelSize(files)) return;
        await submit(
          files,
          name,
          content,
          authors?.split(","),
          source,
          license,
          selected_tags,
        );
      } else {
        await submit(
          //files,
          name,
          content,
          authors?.split(","),
          source,
          license,
          selected_tags,
        );
      }
      document.getElementById("ingest-model").checked = false;
      // name = "";
      // authors = "";
      // source = "";
      // license = "";
      // content = "";
      // files = null;
      // input.value = ""; // reset files in input
      // selected_tags = [];
    } catch (e) {
      // alert(e.message);
      error = e.message;
    }
    loading = false;
  };

  const validateModelSize = (files) => {
    let totalSize = 0;
    for (let i = 0; i < files.length; i++) {
      totalSize += files[i].size;
    }
    if (totalSize < 500 * 1024 * 1024)
      return true; //max 500MB
    else {
      alert(
        "Size must be les than 500MB, current size: " +
          Math.round((totalSize / 1024 / 1024) * 100) / 100 +
          "MB",
      );
      return false;
    }
  };
  const validate_source = (link) => {
    if (!link.startsWith("http://") && !link.startsWith("https://")) {
      alert("Link should start with http:// or https://");
      return false;
    }
    return true;
  };

  const toggleTag = (tag) => {
    if (selected_tags.includes(tag)) {
      selected_tags = selected_tags.filter((t) => t !== tag);
    } else {
      selected_tags = [...selected_tags, tag];
    }
  };
</script>

<label for="ingest-model" class="btn btn-ghost btn-outline">{text}</label>
<input type="checkbox" id="ingest-model" class="modal-toggle" />
<div class="modal">
  <form
    on:submit|preventDefault={ingest}
    class="flex flex-col gap-2 text-sm modal-box w-[95%] sm:w-[75%] max-w-none"
  >
    <slot />
    <span>
      <p>Name</p>
      <input
        class="w-full input input-bordered"
        type="text"
        placeholder="Model name"
        {required}
        bind:value={name}
      />
      <p class="text-sm text-gray-400">*Name should be unique</p>
    </span>
    {#if quality == 0}
      <span>
        <p>Authors (use comma for multiple authors)</p>
        <input
          class="w-full input input-bordered"
          type="text"
          placeholder="Model authors"
          {required}
          bind:value={authors}
        />
        <p class="text-sm text-gray-400">
          *If you are not the author, provide the correct attribution
        </p>
      </span>
      <span>
        <p>Link to source data</p>
        <input
          class="w-full input input-bordered"
          type="text"
          placeholder="Link to source data"
          {required}
          bind:value={source}
        />
        <p class="text-sm text-gray-400">
          *Link to the original source of the data.
        </p>
      </span>
      <span>
        <p>License</p>
        <input
          class="w-full input input-bordered"
          type="text"
          placeholder="License"
          {required}
          bind:value={license}
        />
        <p class="text-sm text-gray-400">*Provide a license for the model.</p>
      </span>
    {/if}
    <p>Description</p>
    <TextEditor bind:content />
    {#if forCreate}
      <p>Files</p>
      <input
        id="uploadfiles"
        class="hidden"
        bind:files
        type="file"
        multiple
        directory
        webkitdirectory
      />
      <label for="uploadfiles" class="btn btn-outline btn-ghost"
        >Select the model directory</label
      >
      {#if files}
        <p class="text-sm text-gray-400">Total files: {files.length}</p>
      {/if}
    {/if}
    <p>Select the appropriate tags:</p>
    <div class="flex flex-wrap gap-1">
      {#each tags as tag}
        <p
          class="badge cursor-pointer text-slate-400 text-xs {selected_tags.includes(
            tag.name,
          )
            ? 'text-slate-200 border-0'
            : 'badge-outline'}"
          on:click={() => toggleTag(tag.name)}
          on:keyup={() => {}}
          style={`${selected_tags.includes(tag.name) && `background-color: ${tag.color};`}`}
        >
          {tag.name}
        </p>
      {/each}
    </div>
    <span class="self-end">
      <label for="ingest-model" class="btn btn-ghost btn-outline btn-error"
        >Close</label
      >
      <button
        class="btn btn-ghost btn-outline {loading && 'loading'}"
        type="submit">Ingest</button
      >
    </span>
    {#if error}
      <p class="text-sm text-error">{error}</p>
    {/if}
  </form>
</div>

<script>
  import Code from "../docs/components/Code.svelte";
  import CLI from "../docs/components/CLI.svelte";
  import TextEditor from "./TextEditor.svelte";
  // import formatFileSize from "../../lib/datasets/formatFileSize.js";

  export let tags;
  export let submit;
  export let text;
  export let required = false;
  export let current_tags = [];
  export let name;
  export let authors;
  export let source;
  export let license;
  export let content;
  export let quality = 0;

  let loading = false;
  let input;
  let error = null;
  $: selected_tags = current_tags;

  const ingest = async () => {
    error = null;
    if (source && !validate_source(source)) return;
    loading = true;
    try {
      if (authors instanceof Array) authors = authors.join(",");
      await submit(
        name,
        content,
        authors?.split(","),
        source,
        license,
        selected_tags
      );
      document.getElementById("ingest-dataset").checked = false;
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

<label for="ingest-dataset" class="btn btn-ghost btn-outline">{text}</label>

<input type="checkbox" id="ingest-dataset" class="modal-toggle" />
<div class="modal">
  <form
    on:submit|preventDefault={ingest}
    class="flex flex-col gap-2 text-sm modal-box"
  >
    {#if quality == 0}
      <slot />
      <span>
        <p>Name</p>
        <input
          class="input input-bordered w-full"
          type="text"
          placeholder="Dataset name"
          {required}
          bind:value={name}
        />
        <p class="text-sm text-gray-400">*Name should be unique</p>
      </span>
      <span>
        <p>Authors (use comma for multiple authors)</p>
        <input
          class="input input-bordered w-full"
          type="text"
          placeholder="Dataset authors"
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
          class="input input-bordered w-full"
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
          class="input input-bordered w-full"
          type="text"
          placeholder="License"
          {required}
          bind:value={license}
        />
        <p class="text-sm text-gray-400">*Provide a license for the dataset.</p>
      </span>
      <p>Description</p>
      <TextEditor bind:content />
      <p>Select the appropriate tags:</p>
      <div class="flex flex-wrap gap-1">
        {#each tags as tag}
          <p
            class="badge badge-outline cursor-pointer text-slate-400 text-xs {selected_tags.includes(
              tag
            ) && 'badge-accent'}"
            on:click={() => toggleTag(tag)}
            on:keyup={() => {}}
          >
            {tag}
          </p>
        {/each}
      </div>
    {/if}
    <span class="self-end">
      <label for="ingest-dataset" class="btn btn-ghost btn-outline btn-error"
        >Close</label
      >
      <button
        class="btn btn-ghost btn-outline {loading && 'loading'}"
        type="submit">Update</button
      >
    </span>
    {#if error}
      <p class="text-sm text-error">{error}</p>
    {/if}
  </form>
</div>

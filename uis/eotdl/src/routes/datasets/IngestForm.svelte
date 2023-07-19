<script>
  import Code from "../docs/components/Code.svelte";
  import CLI from "../docs/components/CLI.svelte";
  import TextEditor from "./TextEditor.svelte";
  import formatFileSize from "../../lib/datasets/formatFileSize.js";

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

  const allowed_extensions = ".zip,.tar,.tar.gz,.csv,.txt,.json,.pdf,.md";
  let loading = false;
  let files = null;
  let input;
  let error = null;
  $: selected_tags = current_tags;
  const ingest = async () => {
    if (source && !validate_source(source)) return;
    loading = true;
    try {
      await submit(
        files,
        name,
        content,
        authors,
        source,
        license,
        selected_tags
      );
      document.getElementById("ingest-dataset").checked = false;
      name = "";
      authors = "";
      source = "";
      license = "";
      content = "";
      files = null;
      input.value = ""; // reset files in input
      selected_tags = [];
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

  let valid_file = true;
  const validate_files = () => {
    if (files?.length == 0) return false;
    if (files.length > 10) {
      files = [];
      input.value = ""; // reset files in input
      alert("Maximum 10 files");
      return false;
    }
    // 1 GB limit
    for (var i = 0; i < files.length; i++) {
      if (files[i].size > 1000000000) valid_file = false;
      else valid_file = true;
    }
    return valid_file;
  };

  const toggleTag = (tag) => {
    if (selected_tags.includes(tag)) {
      selected_tags = selected_tags.filter((t) => t !== tag);
    } else {
      selected_tags = [...selected_tags, tag];
    }
  };

  const reset = () => {
    name = "";
    author = "";
    link = "";
    license = "";
    content = "";
    files = null;
    input.value = ""; // reset files in input
    selected_tags = [];
    error = null;
  };
</script>

<label for="ingest-dataset" class="btn btn-ghost btn-outline">{text}</label>

<input type="checkbox" id="ingest-dataset" class="modal-toggle" />
<div class="modal">
  <form
    on:submit|preventDefault={ingest}
    class="flex flex-col gap-2 text-sm modal-box"
  >
    <slot />
    <input
      type="file"
      accept={allowed_extensions}
      bind:files
      bind:this={input}
      {required}
      multiple
      on:change={validate_files}
    />
    {#if !valid_file}
      <CLI>
        The file size limit is 1GB. Please, use the CLI to ingest larger files:
        <Code>eotdl datasets ingest {`<dataset-path>`}</Code>
        Instruction to install the CLI
        <a
          class="text-green-200 hover:underline"
          href="/docs/getting-started/install">here</a
        >
      </CLI>
    {:else}
      {#if files?.length > 0}
        {#each files as file}
          <p class="text-sm text-gray-400">
            {file.name} ({formatFileSize(file.size)})
          </p>
        {/each}
      {/if}
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
        <p>Author</p>
        <input
          class="input input-bordered w-full"
          type="text"
          placeholder="Dataset author"
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
          *Link to the original source of the data (if available).
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
      <label
        for="ingest-dataset"
        on:click={reset}
        class="btn btn-ghost btn-outline btn-error">Close</label
      >
      <button
        class="btn btn-ghost btn-outline {loading && 'loading'}"
        disabled={!valid_file}
        type="submit">Ingest</button
      >
    </span>
    {#if error}
      <p class="text-sm text-error">{error}</p>
    {/if}
  </form>
</div>

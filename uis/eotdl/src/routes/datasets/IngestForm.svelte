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

    let content = "";
    let loading = false;
    let name = "",
        author = "",
        link = "",
        license = "",
        files = null;
    $: selected_tags = current_tags;
    const ingest = async () => {
        if (files && files[0] && !validate_file(files[0])) return;
        if (link && !validate_link(link)) return;
        loading = true;
        // try {
        await submit(
            files ? files[0] : null,
            name,
            content,
            author,
            link,
            license,
            selected_tags
        );
        document.getElementById("ingest-dataset").checked = false;
        name = "";
        // } catch (e) {
        //     alert(e.message);
        // }
        loading = false;
    };

    const validate_link = (link) => {
        if (!link.startsWith("http://") && !link.startsWith("https://")) {
            alert("Link should start with http:// or https://");
            return false;
        }
        return true;
    };

    let valid_file = true;
    let file_size = null;
    const validate_file = (file) => {
        // 1 GB limit
        file_size = file.size;
        if (file.size > 1000000000) valid_file = false;
        else valid_file = true;
        return valid_file;
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
<label for="ingest-dataset" class="modal cursor-pointer">
    <label class="modal-box relative" for="">
        <form on:submit|preventDefault={ingest} class="flex flex-col gap-2">
            <slot />
            <input
                type="file"
                accept=".zip"
                bind:files
                {required}
                on:change={(e) => validate_file(e.target.files[0])}
            />
            <p>{file_size ? "File size: " + formatFileSize(file_size) : ""}</p>
            {#if !valid_file}
                <CLI>
                    You are trying to upload a big dataset. Please, use the CLI
                    instead:
                    <Code>eotdl-cli datasets ingest {`<dataset-path>`}</Code>
                    Instruction to install the CLI
                    <a
                        class="text-green-200 hover:underline"
                        href="/docs/getting-started/install">here</a
                    >
                </CLI>
            {:else}
                <span>
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
                    <input
                        class="input input-bordered w-full"
                        type="text"
                        placeholder="Dataset author"
                        {required}
                        bind:value={author}
                    />
                    <p class="text-sm text-gray-400">
                        *If you are not the author, provide the correct
                        attribution
                    </p>
                </span>
                <span>
                    <input
                        class="input input-bordered w-full"
                        type="text"
                        placeholder="Link to source data"
                        {required}
                        bind:value={link}
                    />
                    <p class="text-sm text-gray-400">
                        *Link to the original source of the data (if available).
                    </p>
                </span>
                <span>
                    <input
                        class="input input-bordered w-full"
                        type="text"
                        placeholder="License"
                        {required}
                        bind:value={license}
                    />
                    <p class="text-sm text-gray-400">
                        *Provide a license for the dataset.
                    </p>
                </span>
                <TextEditor bind:content />
                <p>Select the appropraite tags:</p>
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
                    class="btn btn-ghost btn-outline btn-error">Close</label
                >
                <button
                    class="btn btn-ghost btn-outline {loading && 'loading'}"
                    disabled={!valid_file}
                    type="submit">Ingest</button
                >
            </span>
        </form>
    </label>
</label>

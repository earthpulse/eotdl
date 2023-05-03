<script>
    import Code from "../docs/components/Code.svelte";
    import CLI from "../docs/components/CLI.svelte";
    import { user, id_token } from "$stores/auth";
    import { datasets } from "../../stores/datasets";
    import TextEditor from "./TextEditor.svelte";

    let content = { html: "", text: "" };
    let loading = false;
    let name = "",
        files = null;
    const ingest = async () => {
        if (name.length === 0 || content.text.length === 0 || files === null)
            return;
        if (!validate_file(files[0])) return;
        loading = true;
        try {
            await datasets.ingest(files[0], name, content.html, $id_token);
            document.getElementById("ingest-dataset").checked = false;
            name = "";
        } catch (e) {
            alert(e.message);
        }
        loading = false;
    };

    let valid_file = true;
    const validate_file = (file) => {
        // 100 MB limit
        if (file.size > 100000000) valid_file = false;
        else valid_file = true;
        return valid_file;
    };
</script>

{#if $user}
    <label for="ingest-dataset" class="btn btn-ghost btn-outline mt-4"
        >+ Ingest Dataset</label
    >
{/if}

<input type="checkbox" id="ingest-dataset" class="modal-toggle" />
<label for="ingest-dataset" class="modal cursor-pointer">
    <label class="modal-box relative" for="">
        <form on:submit|preventDefault={ingest} class="flex flex-col gap-2">
            <h3 class="text-lg font-bold">Ingest dataset</h3>
            <input
                type="file"
                accept=".zip"
                required
                bind:files
                on:change={(e) => validate_file(e.target.files[0])}
            />
            <span>
                <input
                    class="input input-bordered w-full"
                    type="text"
                    placeholder="Dataset name"
                    required
                    bind:value={name}
                />
                <p class="text-sm text-gray-400">*Name should be unique</p>
            </span>
            <TextEditor bind:content />
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

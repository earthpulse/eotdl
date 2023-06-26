<script>
    import { user, id_token } from "$stores/auth";
    import { datasets } from "../../stores/datasets";
    import IngestForm from "./IngestForm.svelte";

    export let tags;

    const submit = async (
        files,
        name,
        content,
        author,
        link,
        license,
        selected_tags
    ) => {
        if (
            !name ||
            files?.length == 0 ||
            !author ||
            !license ||
            !link ||
            !content ||
            content.length == 0
        )
            throw new Error("Please fill in all fields");
        let data;
        if (files.length == 0) throw new Error("Please upload a file");
        const datasetExists = $datasets.data.find(
            (d) => d.name == name && d.uid == $user.uid
        );
        if (datasetExists)
            throw new Error("Dataset already exists, choose a different name");
        for (var i = 0; i < files.length; i++) {
            data = await datasets.ingest(files[i], name, $id_token);
        }
        await datasets.update(
            data.id,
            null,
            content,
            author,
            link,
            license,
            selected_tags,
            $id_token
        );
    };
</script>

{#if $user}
    <IngestForm {tags} {submit} text="+ Ingest dataset" required={true}>
        <h3 class="text-lg font-bold">Ingest dataset</h3>
    </IngestForm>
{/if}

<script>
    import { user, id_token } from "$stores/auth";
    import { datasets } from "../../stores/datasets";
    import IngestForm from "./IngestForm.svelte";

    export let tags;

    const submit = async (
        files,
        name,
        content,
        authors,
        source,
        license,
        selected_tags,
    ) => {
        if (
            !name ||
            files?.length == 0 ||
            authors.length == 0 ||
            !license ||
            !source ||
            !content ||
            content.length == 0
        )
            throw new Error("Please fill in all fields");
        let data;
        if (files.length == 0) throw new Error("Please upload a file");
        const datasetExists = $datasets.data.find(
            (d) => d.name == name && d.uid == $user.uid,
        );
        if (datasetExists)
            throw new Error("Dataset already exists, choose a different name");
        const dataset_id = await datasets.create(
            name,
            authors,
            source,
            license,
            $id_token,
        );
        const version = await datasets.setVersion(dataset_id, $id_token);
        for (var i = 0; i < files.length; i++) {
            data = await datasets.ingest(
                dataset_id,
                files[i],
                $id_token,
                version,
                name,
            );
        }
        await datasets.update(
            dataset_id,
            name,
            content,
            authors,
            source,
            license,
            selected_tags,
            $id_token,
        );
    };
</script>

{#if $user}
    <IngestForm
        {tags}
        {submit}
        text="Ingest dataset"
        forCreate={true}
        required={true}
        name={""}
        authors={""}
        source={""}
        license={""}
        content={""}
    >
        <h3 class="text-lg font-bold">Ingest dataset</h3>
    </IngestForm>
{/if}

<script>
    import { user, id_token } from "$stores/auth";
    import { models } from "../../stores/models";
    import IngestForm from "./IngestForm.svelte";

    export let tags;

    const submit = async (
        files,
        name,
        content,
        authors,
        source,
        license,
        selected_tags
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
        const modelExists = $models.data.find(
            (d) => d.name == name && d.uid == $user.uid
        );
        if (modelExists)
            throw new Error("Model already exists, choose a different name");
        const model_id = await models.create(
            name,
            authors,
            source,
            license,
            $id_token
        );
        const version = await models.setVersion(model_id, $id_token);
        for (var i = 0; i < files.length; i++) {
            data = await models.ingest(model_id, files[i], $id_token, version, name);
        }
        await models.update(
            model_id,
            name,
            content,
            authors,
            source,
            license,
            selected_tags,
            $id_token
        );
    };
</script>

{#if $user}
    <IngestForm 
    {tags} 
    {submit} 
    text="Ingest model" 
    forCreate={true} 
    required={true}
    name={""}
    authors={""}
    source={""}
    license={""}
    content={""}>
        <h3 class="text-lg font-bold">Ingest model</h3>
    </IngestForm>
{/if}

<script>
    import { user, id_token } from "$stores/auth";
    import th from "date-fns/locale/th";
    import { datasets } from "../../stores/datasets";
    import IngestForm from "./IngestForm.svelte";

    export let tags;

    const submit = async (
        file,
        name,
        content,
        author,
        link,
        license,
        selected_tags
    ) => {
        if (
            !name ||
            !file ||
            !author ||
            !license ||
            !link ||
            !content ||
            content.length == 0
        )
            throw new Error("Please fill in all fields");
        await datasets.ingest(
            file,
            name,
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

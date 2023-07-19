<script>
	import { user, id_token } from "$stores/auth";
	import { datasets } from "../../../stores/datasets";
	import IngestForm from "../IngestForm.svelte";
	import { goto } from "$app/navigation";

	export let tags;
	export let dataset_id;
	export let current_tags;
	export let name;
	export let authors;
	export let license;
	export let description;
	export let source;
	export let selected_tags;
	export let size;
	export let files;

	const submit = async (
		_files,
		name,
		content,
		_authors,
		_source,
		_license,
		_selected_tags
	) => {
		const current = $datasets.data.find((d) => d.id == dataset_id);
		if (_files?.length > 0)
			for (var i = 0; i < _files.length; i++) {
				await datasets.ingest(_files[i], current.name, $id_token);
			}
		if (current.name == name) name = null;
		const data = await datasets.update(
			dataset_id,
			name,
			content,
			_authors,
			_source,
			_license,
			_selected_tags,
			$id_token
		);
		if (_authors) authors = _authors;
		if (_source) source = _source;
		if (_license) license = _license;
		if (content) description = content;
		size = data.size;
		files = data.files;
		selected_tags = _selected_tags;
		if (name) goto(`/datasets/${name}`, { replaceState: true });
	};
</script>

{#if $user}
	<IngestForm
		{tags}
		{submit}
		text="EDIT"
		{current_tags}
		content={description}
		{authors}
		{source}
		{license}
		{name}
	>
		<h3 class="text-lg font-bold">Edit dataset</h3>
		<p>
			⚠ You can overwrite existing files by uploading a new file with the
			same name.
		</p>
	</IngestForm>
{/if}

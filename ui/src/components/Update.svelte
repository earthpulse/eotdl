<script>
	import { user, id_token } from "$stores/auth";
	import IngestForm from "../routes/datasets/IngestForm.svelte";
	import { goto } from "$app/navigation";

	export let tags;
	export let id;
	export let current_tags;
	export let name;
	export let authors;
	export let license;
	export let description;
	export let source;
	export let selected_tags;
	export let quality;
	export let store;
	export let route;

	const submit = async (
		_name,
		content,
		_authors,
		_source,
		_license,
		_selected_tags
	) => {
		// const current = $datasets.data.find((d) => d.id == id);
		// if (current.name == name) name = null;
		const data = await store.update(
			id,
			_name,
			content,
			_authors,
			_source,
			_license,
			_selected_tags,
			$id_token
		);
		if (_name) name = _name;
		if (_authors) authors = _authors;
		if (_source) source = _source;
		if (_license) license = _license;
		if (content) description = content;
		selected_tags = _selected_tags;
		if (name) goto(`/${route}/${name}`, { replaceState: true });
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
		{quality}
	>
		<h3 class="text-lg font-bold">Edit</h3>
		<!-- <p>
			⚠ You can overwrite existing files by uploading a new file with the
			same name.
		</p> -->
	</IngestForm>
{/if}

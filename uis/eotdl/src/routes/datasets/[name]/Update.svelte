<script>
	import { user, id_token } from "$stores/auth";
	import { datasets } from "../../../stores/datasets";
	import IngestForm from "../IngestForm.svelte";
	import { goto } from "$app/navigation";

	export let tags;
	export let dataset_id;
	export let current_tags;
	export let name;
	export let author;
	export let license;
	export let description;
	export let link;
	export let selected_tags;
	export let size;
	export let checksum;

	const submit = async (
		file,
		name,
		content,
		_author,
		_link,
		_license,
		_selected_tags
	) => {
		const data = await datasets.reupload(
			dataset_id,
			file,
			name,
			content,
			_author,
			_link,
			_license,
			_selected_tags,
			$id_token
		);
		if (_author) author = _author;
		if (_link) link = _link;
		if (_license) license = _license;
		if (content) description = content;
		if (file) size = file.size;
		selected_tags = _selected_tags;
		checksum = data.checksum;
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
		{author}
		{link}
		{license}
		{name}
	>
		<h3 class="text-lg font-bold">Edit dataset</h3>
		<p>⚠ This operation will overwrite your current data!</p>
	</IngestForm>
{/if}

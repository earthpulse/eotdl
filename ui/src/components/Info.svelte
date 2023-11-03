<script>
	import { parseISO, formatDistanceToNow } from "date-fns";
	import Download from "svelte-material-icons/CloudDownloadOutline.svelte";
	import Sd from "svelte-material-icons/Sd.svelte";
	import formatFileSize from "$lib/datasets/formatFileSize.js";
	import CheckDecagramOutline from "svelte-material-icons/CheckDecagramOutline.svelte";
	import { user, id_token } from "$stores/auth";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";

	export let data;
	export let version;
	export let store;
	export let field = "liked_datasets";

	$: ({ likes, downloads, quality, versions, createdAt } = data);

	const like = () => {
		if (!$user) return;
		store.like(data.id, $id_token);
		if ($user[field].includes(data.id)) {
			$user[field] = $user[field].filter((d) => d !== data.id);
			data.likes = data.likes - 1;
		} else {
			$user[field] = [...$user[field], data.id];
			data.likes = data.likes + 1;
		}
	};

	$: version = versions[versions.length - 1];
</script>

<p class="text-gray-400">
	Created {formatDistanceToNow(parseISO(createdAt))} ago
</p>
<span class="text-gray-400 flex flex-row gap-3 items-center">
	<span class="flex flex-row gap-1">
		<button on:click={like}>
			<HeartOutline
				color={$user && $user[field]?.includes(data.id)
					? "red"
					: "gray"}
			/>
		</button>
		<p>{likes}</p>
	</span>
	<span class="flex flex-row items-center gap-1">
		<Download color="gray" size={20} />
		<p>{downloads}</p>
	</span>
	<span class="flex flex-row items-center gap-1">
		<Sd color="gray" size={20} />
		<p>{formatFileSize(version.size)}</p>
	</span>
	<span class="flex flex-row items-center gap-1">
		<CheckDecagramOutline color="gray" size={20} />
		<p>Q{quality}</p>
	</span>
</span>
<span class="flex flex-row gap-3">
	<p>Version:</p>
	<select
		class="border w-10 select-accent"
		on:change={(e) => {
			const version_id = e.target.value;
			version = versions.find((v) => v.version_id == version_id);
		}}
	>
		{#each versions as version}
			<option
				value={version.version_id}
				selected={version.version_id == version.version_id}
			>
				{version.version_id}
			</option>
		{/each}
	</select>
	<p class="text-gray-400">
		Created {formatDistanceToNow(parseISO(version.createdAt))} ago
	</p>
</span>

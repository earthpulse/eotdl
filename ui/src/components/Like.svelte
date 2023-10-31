<script>
	import { user, id_token } from "$stores/auth";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";

	export let data;
	export let store;
	export let field = "liked_datasets";

	const like = () => {
		if (!$user) return;
		store.like(dataset.id, $id_token);
		if ($user[field].includes(data.id)) {
			$user[field] = $user[field].filter((d) => d !== data.id);
			data.likes = data.likes - 1;
		} else {
			$user[field] = [...$user[field], data.id];
			data.likes = data.likes + 1;
		}
	};
</script>

<button on:click={like}>
	<HeartOutline color={$user[field]?.includes(data.id) ? "red" : "gray"} />
</button>

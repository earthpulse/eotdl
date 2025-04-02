<script>
	import { models } from "$stores/models";
	import auth from "$stores/auth.svelte";
	import Card from "$components/Card.svelte";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import { browser } from "$app/environment";
	import Pagination from "$components/Pagination.svelte";
	import Tags from "$components/Tags.svelte";
	import Skeleton from "$components/Skeleton.svelte";
	import ModelsLeaderboard from "../ModelsLeaderboard.svelte";
	// import Ingest from "./Ingest.svelte";

	let { data } = $props();

	let loading = $state(true);
	let show_liked = $state(false);
	let selected_tags = $state([]);
	let selected_qualities = $state([]);

	const load = async () => {
		await models.retrieve(fetch);
		loading = false;
		show_liked = localStorage.getItem("show_liked") === "true";
		filtered_models = JSON.parse(localStorage.getItem("filtered_models"));
		selected_tags = JSON.parse(localStorage.getItem("selected_tags")) || [];
	};

	$effect(() => {
		load();
	});

	let filterName = $state("");
	let filtered_models = $state(null);
	$effect(() => {
		filtered_models = $models.data
			?.filter((models) => {
				if (selected_tags.length === 0) return true;
				return selected_tags.every((tag) =>
					models.tags.includes(tag.name),
				);
			})
			.filter((models) => {
				if (filterName.length === 0) return true;
				return models.name
					.toLowerCase()
					.includes(filterName.toLowerCase());
			});
		if (show_liked) {
			filtered_models = filtered_models.filter((models) =>
				auth.user?.liked_models.includes(models.id),
			);
		}
		if (selected_qualities.length > 0) {
			filtered_models = filtered_models?.filter((model) =>
				selected_qualities?.includes(model.quality),
			);
		}
	});

	const toggleLike = () => {
		show_liked = auth.user && !show_liked;
		localStorage.setItem("show_liked", show_liked);
	};

	const onToggleTag = (tags) =>
		localStorage.setItem("selected_tags", JSON.stringify(tags));
</script>

<svelte:head>
	<title>EOTDL | Models</title>
</svelte:head>

<div class="w-full flex flex-col items-center justify-between h-full grow">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="grid grid-cols-1 sm:grid-cols-[250px,auto] gap-8 w-full">
			<div class="flex flex-col w-full">
				<div class="flex flew-row justify-between text-3xl">
					<h1 class="font-bold">Models</h1>
					<p class="text-gray-400">
						{loading ? "" : filtered_models?.length}
					</p>
				</div>
				<input
					class="input input-bordered max-w-full input-xs"
					type="text"
					placeholder="Filter by name"
					bind:value={filterName}
				/>
				<span class="flex flew-row justify-between mt-1 mb-3">
					<!-- <p
						class="text-gray-400 hover:underline cursor-pointer text-sm"
					>
						advanced filtering
					</p> -->
					<button onclick={toggleLike}
						><HeartOutline
							color={show_liked ? "red" : "gray"}
						/></button
					>
				</span>
			</div>
			<Tags tags={data?.tags} bind:selected_tags {onToggleTag} />
		</div>
		<!-- <span class="flex flex-row w-full justify-between items-center">
			<Ingest tags={data?.tags} />
		</span> -->
		{#if loading}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each new Array(30) as _}
					<Skeleton />
				{/each}
			</div>
		{:else if filtered_models?.length > 0}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each filtered_models as model, i}
					<Card
						data={model}
						link="models"
						liked={auth.user?.liked_models?.includes(model.id)}
						tags={data.tags}
					/>
				{/each}
			</div>
		{:else}
			<p class="text-gray-400 text-center">No models found</p>
		{/if}
	</div>
	<ModelsLeaderboard />
</div>

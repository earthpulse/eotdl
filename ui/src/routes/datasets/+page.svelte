<script>
	import { datasets } from "$stores/datasets";
	import { user } from "$stores/auth";
	import Card from "$components/Card.svelte";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import { browser } from "$app/environment";
	import Ingest from "./Ingest.svelte";
	import Pagination from "$components/Pagination.svelte";
	import Tags from "$components/Tags.svelte";
	import Skeleton from "$components/Skeleton.svelte";
	import DatasetsLeaderboard from "../DatasetsLeaderboard.svelte";
	import QualitySelector from "$components/QualitySelector.svelte";
	export let data;
	import { links } from "$stores/images";
	let loading = true;
	let show_liked = false;
	let selected_tags = [];

	const load = async () => {
		await datasets.retrieve(fetch);
		loading = false;
		show_liked = localStorage.getItem("show_liked") === "true";
		filtered_datasets = JSON.parse(
			localStorage.getItem("filtered_datasets"),
		);
		selected_tags = JSON.parse(localStorage.getItem("selected_tags")) || [];
	};

	$: if (browser) load();

	let filterName = "";
	let filtered_datasets;
	let selected_qualities = [];
	$: {
		filtered_datasets = $datasets.data
			?.filter((dataset) => {
				if (selected_tags.length === 0) return true;
				return selected_tags.every((tag) => dataset.tags.includes(tag));
			})
			.filter((dataset) => {
				if (filterName.length === 0) return true;
				return dataset.name
					.toLowerCase()
					.includes(filterName.toLowerCase());
			});
		if (show_liked) {
			filtered_datasets = filtered_datasets.filter((dataset) =>
				$user?.liked_datasets.includes(dataset.id),
			);
		}
		if (selected_qualities.length > 0) {
			filtered_datasets = filtered_datasets?.filter((dataset) =>
				selected_qualities?.includes(dataset.quality),
			);
		}
	}

	const toggleLike = () => {
		show_liked = $user && !show_liked;
		localStorage.setItem("show_liked", show_liked);
	};

	const onToggleTag = (tags) =>
		localStorage.setItem("selected_tags", JSON.stringify(tags));
</script>

<svelte:head>
	<title>EOTDL | Datasets</title>
</svelte:head>

<div class="w-full flex flex-col items-center justify-between h-full grow">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="grid grid-cols-1 sm:grid-cols-[250px,auto] gap-8 w-full">
			<div class="flex flex-col w-full">
				<div class="flex flew-row justify-between text-3xl">
					<h1 class="font-bold">Datasets</h1>
					<p class="text-gray-400">
						{loading ? "" : filtered_datasets?.length}
					</p>
				</div>
				<input
					class="input input-bordered max-w-full input-xs"
					type="text"
					placeholder="Filter by name"
					bind:value={filterName}
				/>
				<span class="flex flew-row justify-between mt-1 mb-3">
					<button on:click={toggleLike}
						><HeartOutline
							color={show_liked ? "red" : "gray"}
						/></button
					>
					<QualitySelector bind:selected_qualities />
				</span>
			</div>
			<Tags tags={data?.tags} bind:selected_tags {onToggleTag} />
		</div>
		<span class="flex flex-row w-full justify-between items-center">
			<Ingest tags={data.tags} />
		</span>
		{#if loading}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each new Array(30) as _}
					<Skeleton />
				{/each}
			</div>
		{:else if filtered_datasets?.length > 0}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each filtered_datasets as dataset, i}
					<Card
						img={links[i % links.length]}
						data={dataset}
						liked={$user?.liked_datasets.includes(dataset.id)}
						tags={data.tags}
					/>
				{/each}
			</div>
		{:else}
			<p class="text-gray-400 text-center">No datasets found</p>
		{/if}
	</div>
	<DatasetsLeaderboard />
</div>

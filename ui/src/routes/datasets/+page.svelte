<script>
	import { datasets } from "../../stores/datasets";
	import { user } from "../../stores/auth";
	import Leaderboard from "./Leaderboard.svelte";
	import Card from "./Card.svelte";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import { browser } from "$app/environment";
	import retrieveDatasetsLeaderboard from "../../lib/datasets/retrieveDatasetsLeaderboard";
	import Ingest from "./Ingest.svelte";
	import Pagination from "./Pagination.svelte";
	import Tags from "./Tags.svelte";
	import Skeleton from "./Skeleton.svelte";

	export let data;

	let leaderboard,
		loading = true;
	let show_liked = false;
	let selected_tags = [];

	const load = async () => {
		await datasets.retrieve(fetch);
		leaderboard = await retrieveDatasetsLeaderboard(fetch);
		loading = false;
		show_liked = localStorage.getItem("show_liked") === "true";
		filtered_datasets = JSON.parse(
			localStorage.getItem("filtered_datasets")
		);
		selected_tags = JSON.parse(localStorage.getItem("selected_tags")) || [];
	};

	$: if (browser) load();

	let filterName = "";
	let filtered_datasets;
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
				$user?.liked_datasets.includes(dataset.id)
			);
		}
	}

	const maxVisibleDatasets = 9;
	let currentPage = 0;
	$: numPages = Math.ceil(filtered_datasets?.length / maxVisibleDatasets);
	$: if (numPages > 0) currentPage = 0;
	$: visible_datasets = filtered_datasets?.slice(
		currentPage * maxVisibleDatasets,
		(currentPage + 1) * maxVisibleDatasets
	);

	const toggleLike = () => {
		show_liked = $user && !show_liked;
		localStorage.setItem("show_liked", show_liked);
	};

	const onToggleTag = (tags) =>
		localStorage.setItem("selected_tags", JSON.stringify(tags));
</script>

<svelte:head>
	<title>EOTDL | Datasets</title>
	<meta
		name="description"
		content="EOTDL is a platform for sharing and discovering training datasets."
	/>
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
					<!-- <p
						class="text-gray-400 hover:underline cursor-pointer text-sm"
					>
						advanced filtering
					</p> -->
					<button on:click={toggleLike}
						><HeartOutline
							color={show_liked ? "red" : "gray"}
						/></button
					>
				</span>
				<!-- <Ingest tags={data?.tags} /> -->
				<a
					href="/docs/datasets/ingest"
					class="text-green-200 hover:underline">Ingest dataset</a
				>
			</div>
			<Tags tags={data?.tags} bind:selected_tags {onToggleTag} />
		</div>
		{#if loading}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each [1, 2, 3, 4, 5, 6, 7, 8, 9] as _}
					<Skeleton />
				{/each}
			</div>
		{:else if visible_datasets?.length > 0}
			<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
				{#each visible_datasets as dataset}
					<Card
						{dataset}
						liked={$user?.liked_datasets.includes(dataset.id)}
					/>
				{/each}
			</div>
		{:else}
			<p class="text-gray-400 text-center">No datasets found</p>
		{/if}
		<Pagination {numPages} bind:currentPage />
	</div>
	<Leaderboard {leaderboard} />
</div>

<script>
	import { datasets } from "$stores/datasets";
	import auth from "$stores/auth.svelte";
	import Card from "$components/Card.svelte";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	// import Ingest from "./Ingest.svelte";
	import Pagination from "$components/Pagination.svelte";
	import Tags from "$components/Tags.svelte";
	import Skeleton from "$components/Skeleton.svelte";
	import DatasetsLeaderboard from "../DatasetsLeaderboard.svelte";
	// import QualitySelector from "$components/QualitySelector.svelte";

	let { data } = $props();

	let loading = $state(true);
	let show_liked = $state(false);
	let selected_tags = $state([]);

	const load = async () => {
		await datasets.retrieve(fetch);
		loading = false;
		show_liked = localStorage.getItem("show_liked") === "true";
		filtered_datasets = JSON.parse(
			localStorage.getItem("filtered_datasets"),
		);
		selected_tags = JSON.parse(localStorage.getItem("selected_tags")) || [];
	};

	$effect(() => {
		load();
	});

	let filterName = $state("");
	let filtered_datasets = $state();
	$effect(() => {
		let base_datasets = $datasets.data || []; // Start with all datasets or an empty array

		// Filter by tags
		let datasets_after_tags = base_datasets.filter((dataset) => {
			if (selected_tags.length === 0) return true;
			return selected_tags.every((tag) => dataset.tags.includes(tag));
		});

		// Filter by name
		let datasets_after_name = datasets_after_tags.filter((dataset) => {
			if (filterName.length === 0) return true;
			return dataset.name
				.toLowerCase()
				.includes(filterName.toLowerCase());
		});

		// Filter by liked status if show_liked is true and user is logged in
		let final_datasets;
		if (show_liked && auth.user) {
			final_datasets = datasets_after_name.filter((dataset) =>
				auth.user.liked_datasets.includes(dataset.id),
			);
		} else {
			final_datasets = datasets_after_name;
		}

		// Assign the final result
		filtered_datasets = final_datasets;
	});

	const toggleLike = () => {
		show_liked = auth.user && !show_liked;
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
		<div class="grid grid-cols-1 sm:grid-cols-[250px_auto] gap-8 w-full">
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
					<button
						onclick={toggleLike}
						class="cursor-pointer hover:scale-115 transition-all duration-200"
						><HeartOutline
							color={show_liked ? "red" : "gray"}
						/></button
					>
				</span>
			</div>
			<Tags tags={data?.tags} bind:selected_tags {onToggleTag} />
		</div>
		<!-- <span class="flex flex-row w-full justify-between items-center">
			<Ingest tags={data.tags} />
		</span> -->
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
						data={dataset}
						liked={auth.user?.liked_datasets.includes(dataset.id)}
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

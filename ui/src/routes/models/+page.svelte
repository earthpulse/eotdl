<script>
	import { models } from "$stores/models";
	import auth from "$stores/auth.svelte";
	import Card from "$components/Card.svelte";
	import HeartOutline from "svelte-material-icons/HeartOutline.svelte";
	import ChevronDown from "svelte-material-icons/ChevronDown.svelte";
	import ChevronUp from "svelte-material-icons/ChevronUp.svelte";
	import { browser } from "$app/environment";
	import Pagination from "$components/Pagination.svelte";
	import Tags from "$components/Tags.svelte";
	import Skeleton from "$components/Skeleton.svelte";
	import ModelsLeaderboard from "../ModelsLeaderboard.svelte";
	// import Ingest from "./Ingest.svelte";
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";

	let { data } = $props();

	let loading = $state(true);
	let show_liked = $state(false);
	let selected_tags = $state([]);
	let selected_qualities = $state([]);
	let current_order_by = $state("created_at");
	let current_order_direction = $state("desc");
	let filterFunctions = $state({
		byName: (model) => {
			if (filterName.length === 0) return true;
			return model.name.toLowerCase().includes(filterName.toLowerCase());
		},
		byDescription: (model) => {
			if (filterName.length === 0) return true;
			return model.metadata.description
				.toLowerCase()
				.includes(filterName.toLowerCase());
		},
	});

	// the value of the key should be the sort function
	let orderBy = $state({
		likes: (a, b) =>
			(b.likes - a.likes) * (current_order_direction === "desc" ? 1 : -1),
		downloads: (a, b) =>
			(b.downloads - a.downloads) *
			(current_order_direction === "desc" ? 1 : -1),
		created_at: (a, b) =>
			(new Date(b.createdAt) - new Date(a.createdAt)) *
			(current_order_direction === "desc" ? 1 : -1),
		size: (a, b) =>
			(b.versions[b.versions.length - 1].size -
				a.versions[a.versions.length - 1].size) *
			(current_order_direction === "desc" ? 1 : -1),
	});

	const load = async () => {
		await models.retrieve(fetch);
		loading = false;
		show_liked = localStorage.getItem("show_liked") === "true";
		const tagsFromURL = $page.url.searchParams.get("tags");
		if (tagsFromURL) {
			selected_tags = tagsFromURL.split(",");
		} else {
			selected_tags = [];
		}
	};

	$effect(() => {
		load();
	});

	let filterName = $state("");
	let filtered_models = $state(null);
	let all_filtered_models = $state();
	$effect(() => {
		let base_models = $models.data || [];
		// Filter by tags
		let models_after_tags = base_models.filter((model) => {
			if (selected_tags.length === 0) return true;
			return selected_tags.every((tag) => model.tags.includes(tag));
		});

		// Filter by name, description, tags, ...
		let models_after_name = models_after_tags.filter(
			filterFunctions.byName,
		);
		all_filtered_models = models_after_name;

		let models_after_description = models_after_tags.filter(
			filterFunctions.byDescription,
		);
		all_filtered_models = models_after_description;
		// Filter by liked status if show_liked is true and user is logged in
		let final_models;
		if (show_liked && auth.user) {
			final_models = models_after_name.filter((model) =>
				auth.user.liked_models.includes(model.id),
			);
			final_datasets?.push(
				...models_after_description.filter((model) =>
					auth.user.liked_models.includes(model.id),
				),
			);
			// Remove duplicated datasets (If the searched text is in the name and description)
			final_models = [...new Set(final_models)];
		} else {
			// Add datasets by description and name
			final_models = models_after_name.concat(models_after_description);
			// Remove duplicated datasets (If the searched text is in the name and description)
			final_models = [...new Set(final_models)];
		}
		filtered_models = final_models.sort(orderBy[current_order_by]);
		// Assign the final result
	});

	const toggleLike = () => {
		show_liked = auth.user && !show_liked;
		localStorage.setItem("show_liked", show_liked);
	};

	const onToggleTag = (tags) => {
		const newURL = new URL($page.url);
		if (tags.length > 0) {
			newURL.searchParams.set("tags", tags.join(","));
		} else {
			newURL.searchParams.delete("tags");
		}
		goto(newURL, { keepFocus: true, noScroll: true });
	};
</script>

<svelte:head>
	<title>EOTDL | Models</title>
</svelte:head>

<div class="w-full flex flex-col items-center justify-between h-full grow">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="grid grid-cols-1 sm:grid-cols-[250px_auto] gap-8 w-full">
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
					placeholder="Filter by name, description, tags, ..."
					bind:value={filterName}
				/>
				<span class="flex flew-row justify-between mt-1 mb-3">
					<div class="flex flex-row gap-1 w-fit items-center">
						<button
							onclick={toggleLike}
							class="cursor-pointer hover:scale-115 transition-all duration-200"
							><HeartOutline
								color={show_liked ? "red" : "gray"}
							/></button
						>
						<a
							href="https://radiantearth.github.io/stac-browser/#/external/api.eotdl.com/stac?.language=en"
							target="_blank"
							class="btn btn-outline btn-xs text-gray-400">STAC</a
						>
					</div>
					<div class="flex flex-row gap-1 w-fit items-center">
						<select
							class="select select-bordered select-xs"
							bind:value={current_order_by}
						>
							<option value="" disabled selected>
								Order by
							</option>
							{#each Object.keys(orderBy) as key}
								<option value={key}
									>{key.charAt(0).toUpperCase() +
										key.slice(1).replace(/_/g, " ")}</option
								>
							{/each}
						</select>
						{#if current_order_direction === "desc"}
							<button
								onclick={() => {
									current_order_direction = "asc";
								}}
							>
								<ChevronDown class="cursor-pointer" />
							</button>
						{:else}
							<button
								onclick={() => {
									current_order_direction = "desc";
								}}
							>
								<ChevronUp class="cursor-pointer" />
							</button>
						{/if}
					</div>
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

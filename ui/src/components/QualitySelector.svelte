<script>
	import { browser } from "$app/environment";

	export let selected_qualities;

	$: if (browser)
		selected_qualities =
			JSON.parse(localStorage.getItem("selected_qualities")) || [];

	let qualities = [0, 1, 2];

	const toggleQuality = (q) => {
		if (selected_qualities.includes(q)) {
			selected_qualities = selected_qualities.filter((qq) => qq !== q);
		} else {
			selected_qualities = [...selected_qualities, q];
		}
		localStorage.setItem(
			"selected_qualities",
			JSON.stringify(selected_qualities)
		);
	};
</script>

<span class="flex flex-row gap-1">
	{#each qualities as quality}
		<button
			class="border b rounded px-1 {selected_qualities.includes(quality)
				? 'text-slate-500 border-green-200 bg-green-100'
				: 'border-gray-400 text-gray-400'}"
			on:click={() => toggleQuality(quality)}>Q{quality}</button
		>
	{/each}
</span>

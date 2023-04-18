<script>
	export let previos_link;
	export let next_link;
</script>

<div class="w-fill flex flex-row justify-between">
	{#if previos_link}
		<a
			class="text-green-200 text-sm hover:underline"
			href={previos_link.link}>{"<"} {previos_link.name}</a
		>
	{:else}
		<p />
	{/if}
	{#if next_link}
		<a class="text-green-200 text-sm hover:underline" href={next_link.link}
			>{next_link.name} {">"}
		</a>
	{:else}
		<p />
	{/if}
</div>

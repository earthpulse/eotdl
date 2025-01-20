<script>
	export let data;

	$: ({ authors, license, source } = data.catalog.eotdl);
</script>

<p>Metadata:</p>
<div class="overflow-auto w-full">
	<table class="table border-2 rounded-lg table-compact h-[100px] w-full">
		<tbody>
			<tr>
				<th class="w-[20px] text-xs">Author(s)</th>
				<td class="text-xs">{authors.join(", ") || "-"}</td>
			</tr>
			<tr>
				<th class="text-xs">License</th>
				<td class="text-xs">{license || "-"}</td>
			</tr>
			<tr>
				<th class="text-xs">Source</th>
				<td>
					{#if source}
						<a
							href={source}
							target="_blank"
							rel="noopener noreferrer"
							class="text-green-200 hover:underline text-xs"
							>{source.length > 30
								? source.slice(0, 30) + "..."
								: source}</a
						>
					{:else}
						-
					{/if}
				</td>
			</tr>
		</tbody>
	</table>
</div>

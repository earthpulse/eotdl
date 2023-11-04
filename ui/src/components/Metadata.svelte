<script>
	export let data;

	$: ({ authors, license, source } = data);
</script>

<p>Metadata:</p>
<div class="overflow-auto w-full">
	<table class="table border-2 rounded-lg table-compact h-[100px] w-full">
		<tbody>
			<tr>
				<th class="w-[20px]">Author(s)</th>
				<td>{authors.join(", ") || "-"}</td>
			</tr>
			<tr>
				<th>License</th>
				<td>{license || "-"}</td>
			</tr>
			<tr>
				<th>Source</th>
				<td>
					{#if source}
						<a
							href={source}
							target="_blank"
							rel="noopener noreferrer"
							class="text-green-200 hover:underline"
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

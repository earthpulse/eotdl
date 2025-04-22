<script>
	import Trash from "svelte-material-icons/TrashCan.svelte";
	export let authors;
	export let license;
	export let source;
	export let edit = false;
</script>

{#if edit}
	<p>Metadata:</p>
	<div class="overflow-auto w-full">
		<table
			class="table border-1 border-gray-200 rounded-lg table-compact h-[100px] w-full"
		>
			<tbody>
				<tr>
					<th class="w-[20px] text-xs">Author(s)</th>
					<td class="text-xs h-fit max-h-24">
						<div class="h-32 overflow-y-auto">
							{#each authors as author, index}
								<div class="flex items-center gap-2 mb-2 ml-2">
									<input
										class="input input-bordered w-full h-fit"
										type="text"
										bind:value={authors[index]}
									/>
									<button
										class=""
										on:click={() =>
											(authors = authors.filter(
												(_, i) => i !== index,
											))}
									>
										<Trash class="size-4" />
									</button>
								</div>
							{/each}
							<button
								class="hover:underline"
								on:click={() => (authors = [...authors, ""])}
							>
								Añadir autor
							</button>
						</div>
					</td>
				</tr>
				<tr>
					<th class="text-xs">License</th>
					<td class="text-xs"
						><input
							class="input input-bordered w-full"
							type="text"
							bind:value={license}
						/></td
					>
				</tr>
				<tr>
					<th class="text-xs">Source</th>
					<td>
						{#if source}
							<p class="text-green-200 hover:underline text-xs">
								<input
									class="input input-bordered w-full"
									type="text"
									bind:value={source}
								/>
							</p>
						{:else}
							-
						{/if}
					</td>
				</tr>
			</tbody>
		</table>
	</div>
{:else}
	<p>Metadata:</p>
	<div class="overflow-auto w-full">
		<table
			class="table border-1 border-gray-200 rounded-lg table-compact h-[100px] w-full"
		>
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
{/if}

<script>
	import { tutorials } from "./tutorials";
</script>

<div class="w-full flex flex-col items-center justify-between h-full grow">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="flex flex-col justify-between mb-6 mt-12 w-full gap-2">
			<h1 class="font-bold text-3xl">Tutorials</h1>
			<p>
				Learn hot to leverage EOTDL with examples, use cases and
				workshops.
			</p>
		</div>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
			{#each tutorials as tutorial}
				<div
					class="border border-gray-200 shadow-lg p-4 rounded-lg flex flex-col h-fit"
				>
					<div class="text-left">
						<h2 class="font-bold mb-2 mt-0 text-lg">
							{tutorial.name}
						</h2>
						<img
							class="w-full h-48 object-cover mb-2"
							src={tutorial.thumbnail}
							alt={tutorial.name}
						/>
						<p class="mb-2 text-sm">{tutorial.description}</p>
					</div>
					<div class="grid grid-cols-1">
						{#each Object.keys(tutorial.links) as key}
							<a
								class="hover:underline text-blue-800"
								href={tutorial.links[key]}
								target="_blank">{key}</a
							>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>

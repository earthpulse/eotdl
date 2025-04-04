<script>
	export let tutorials;
</script>

<div class="flex flex-col items-center w-full mb-12">
	<div class="gap-3 w-full max-w-6xl text-center flex flex-col px-4">
		<h1
			class="font-bold text-3xl w-full text-left pb-6 text-[rgb(74,191,167)] uppercase"
		>
			Tutorials
		</h1>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
			{#each tutorials as tutorial}
				<a
					href={tutorial.links[Object.keys(tutorial.links)[0]]}
					class="bg-white rounded-lg shadow-xl overflow-hidden border-1 border-gray-200 transition-transform duration-200 hover:scale-105"
				>
					<img
						src={tutorial.thumbnail}
						alt={tutorial.name}
						class="w-full h-48 object-cover rounded-t-lg"
					/>
					<div class="p-4 bg-gray-100 h-full">
						<h2 class="text-xl font-semibold mb-2 text-left">
							{tutorial.name}
						</h2>
						<p class="text-gray-600 text-left">
							{tutorial.description}
						</p>
					</div>
				</a>
			{/each}
		</div>
	</div>
</div>

<script>
	const applications = [
		{
			name: "Tutorial test",
			thumbnail: "",
			description:"Lorem ipsum dolor sit amet consectetur adipisicing elit. Accusantium debitis voluptates corporis enim mollitia voluptatum officia impedit minus sit, modi, nesciunt perspiciatis fuga eum molestias eaque similique alias, quos vel.",
			link: "https://hub.api.eotdl.com/",
		},
	];
</script>

<div class="w-full flex flex-col items-center justify-between h-full grow">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="flex flex-col justify-between mb-6 w-full gap-2">
			<h1 class="font-bold text-3xl">Tutorials</h1>
			<p>
				Tutorials.
			</p>
		</div>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full mt-3">
			{#each applications as application}
				<div
					class="border border-gray-200 shadow-lg p-4 rounded-lg flex flex-col justify-between"
				>
					<div class="text-left">
						<h2 class="font-bold mb-2 mt-0 text-lg">
							{application.name}
						</h2>
						<img
							class="w-full h-48 object-cover mb-2"
							src={application.thumbnail}
							alt={application.name}
						/>
						<p class="mb-2 text-sm">{application.description}</p>
					</div>
					<div class="text-right">
						<a
							href={application.link}
							target="_blank"
							rel="noopener"
						>
							<button class="btn btn-outline"> Open </button>
						</a>
					</div>
				</div>
			{/each}
		</div>
	</div>
</div>

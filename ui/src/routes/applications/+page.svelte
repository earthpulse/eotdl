<script>
	const applications = [
		{
			name: "EOx Cloud Workspace",
			thumbnail: "/applications/workspace.png",
			description:
				"Create training datasets and train ML-models in the cloud with the EOx Cloud Workspace, included for free to all EOTDL users.",
			link: "https://hub.api.eotdl.com/",
		},
		{
			name: "SCANEO",
			thumbnail: "/applications/scaneo.png",
			description:
				"SCANEO is a web-based application that allows users to visualize and labell satellite data, with tight integration with the EOTDL API and AI assited capabilities for Active Learning.",
			link: "https://pypi.org/project/scaneo/",
		},
		{
			name: "PytorchEO",
			thumbnail: "/applications/peo.png",
			description:
				"PytorchEO is an open-source library to streamline the design and training of Deep Learning models with EO data. It offers wrappers to EOTDL datasets and models.",
			link: "https://github.com/earthpulse/pytorchEO",
		},
	];
</script>

<div class="w-full flex flex-col items-center justify-between h-full grow">
	<div
		class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col items-center h-full"
	>
		<div class="grid grid-cols-1 sm:grid-cols-[250px,auto] gap-8 w-full">
			<div class="flex flex-col w-full">
				<div class="flex flew-row justify-between text-3xl mb-6">
					<h1 class="font-bold">Applications</h1>
				</div>
			</div>
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
		<p class="text-sm mt-6 text-left w-full">
			If you want your application to appear here, please get in touch
			with us through <a
				href="https://discord.gg/hYxc5AJB92"
				class="hover:underline text-green-200">Discord</a
			>.
		</p>
	</div>
</div>

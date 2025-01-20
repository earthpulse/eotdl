<script>
	const applications = [
		{
			name: "EOx Cloud Workspace",
			thumbnail: "/applications/workspace.png",
			description:
				"Create training datasets and train ML-models in the cloud with the EOx Cloud Workspace, included for free to all EOTDL users. Get in touch with us if you require GPUs for your workloads.",
			link: "https://hub.api.eotdl.com/",
		},
		{
			name: "SCANEO",
			thumbnail: "/applications/scaneo.png",
			description:
				"SCANEO is a web-based application that allows users to visualize and labell satellite data, with tight integration with the EOTDL API and AI assited capabilities for Active Learning. Learn more <a href='https://github.com/earthpulse/scaneo' target='_blank' class='underline'>here</a>. <b>IMPORTANT:</b> SCANEO is only available in the EOTDL Cloud Workspace for Premium users.",
			link: "https://hub.api.eotdl.com/services/eoxhub-gateway/eotdl/scaneo/",
		},
		{
			name: "AI4EO Challenges",
			thumbnail: "/applications/ai4eo.png",
			description:
				"AI4EO is dedicated to organising cutting-edge artificial intelligence-based challenges in partnership with esteemed partners and sponsors. Compete, learn and win amazing prizes!",
			link: "https://platform.ai4eo.eu/",
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
		<div class="flex flex-col justify-between mb-6 w-full gap-2">
			<h1 class="font-bold text-3xl">Applications</h1>
			<p>
				Third party applications leverage EOTDL to offer additional
				features such as cloud computing resources, data labelling, and
				more.
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
						<p class="mb-2 text-sm">
							{@html application.description}
						</p>
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

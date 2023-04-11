<script>
	import { page } from "$app/stores";

	const links = [
		{
			group: "Getting Started",
			link: "getting-started",
			links: [{ name: "Introduction", link: "introduction" }],
		},
		{
			group: "Datasets",
			link: "datasets",
			links: [
				{ name: "Explore", link: "explore" },
				{ name: "Download", link: "download" },
				{ name: "Ingest", link: "ingest" },
			],
		},
		// {
		// 	group: "Models",
		// 	link: "models",
		// 	links: [
		// 		{ name: "Explore", link: "explore" },
		// 		{ name: "Download", link: "download" },
		// 	],
		// },
		// {
		// 	group: "Training",
		// 	link: "training",
		// },
		{
			group: "Contributing",
			link: "contributing",
		},
	];
</script>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-10 mt-10 max-w-6xl flex flex-col gap-5">
		<a class="text-3xl font-bold hover:underline" href="/docs"
			>Documentation</a
		>
		<div class="flex flex-row gap-3">
			<ul class="list pr-3 w-[200px]">
				{#each links as link}
					<li class="pb-3">
						<a
							class="font-bold hover:underline {$page.route.id ===
							`/docs/${link.link}`
								? ''
								: 'text-slate-500'}"
							href={`/docs/${link.link}`}>{link.group}</a
						>
						{#if link.links?.length > 0}
							<ul>
								{#each link.links as _link}
									<li
										class="hover:underline {$page.route
											.id ===
										`/docs/${link.link}/${_link.link}`
											? 'text-slate-600'
											: 'text-slate-300'}"
									>
										<a
											href={`/docs/${link.link}/${_link.link}`}
											>{_link.name}</a
										>
									</li>
								{/each}
							</ul>
						{/if}
					</li>
				{/each}
			</ul>
			<div>
				<slot />
			</div>
		</div>
	</div>
</div>

<style>
	.list {
		border-right: 1px solid rgb(185, 185, 185);
	}
</style>

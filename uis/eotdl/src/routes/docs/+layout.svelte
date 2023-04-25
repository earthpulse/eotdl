<script>
	import { page } from "$app/stores";
	import "../../styles/docs.css";
	import Nav from "./Nav.svelte";

	const links = [
		{
			group: "Getting Started",
			link: "getting-started",
			links: [
				{ name: "Install", link: "install" },
				{ name: "Authenticate", link: "authenticate" },
			],
		},
		{
			group: "Datasets",
			link: "datasets",
			links: [
				{ name: "Quality Levels", link: "quality" },
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

	const links_ordered_list = [
		{ name: "Documentation", link: "/docs" },
		...links
			.map((link) => {
				if (link.links?.length > 0)
					return [
						{ name: link.group, link: `/docs/${link.link}` },
						...link.links?.map((l) => ({
							name: l.name,
							link: `/docs/${link.link}/${l.link}`,
						})),
					];
				return [{ name: link.group, link: `/docs/${link.link}` }];
			})
			.flat(),
	];

	$: previos_link =
		links_ordered_list[
			links_ordered_list.map((l) => l.link).indexOf($page.route.id) - 1
		];
	$: next_link =
		links_ordered_list[
			links_ordered_list.map((l) => l.link).indexOf($page.route.id) + 1
		];
</script>

<div class="w-full min-w-6xl flex flex-col items-center">
	<div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-5">
		<a class="text-3xl font-bold hover:underline" href="/docs"
			>Documentation</a
		>
		<div class="grid grid-cols-[200px,auto]">
			<div class="list pr-3">
				{#each links as link}
					<span class="pb-3 flex flex-col gap-2">
						<a
							class="font-bold hover:underline border-l-2 pl-2 -translate-x-2 text-sm {$page
								.route.id === `/docs/${link.link}`
								? 'text-green-200  border-green-200'
								: 'text-slate-500 border-white'}"
							href={`/docs/${link.link}`}>{link.group}</a
						>
						{#if link.links?.length > 0}
							<div class="pb-3 flex flex-col gap-2">
								{#each link.links as _link}
									<span
										class="flex flex-col hover:underline border-l-2 pl-2 -translate-x-2 text-sm {$page
											.route.id ===
										`/docs/${link.link}/${_link.link}`
											? 'text-green-200  border-green-200'
											: 'text-slate-300 border-white'}"
									>
										<a
											href={`/docs/${link.link}/${_link.link}`}
											>{_link.name}</a
										>
									</span>
								{/each}
							</div>
						{/if}
					</span>
				{/each}
			</div>
			<div class="flex flex-col px-3 gap-3 w-full">
				<Nav {previos_link} {next_link} />
				<slot />
				<Nav {previos_link} {next_link} />
			</div>
		</div>
	</div>
</div>

<style>
	.list {
		border-right: 1px solid rgba(185, 185, 185, 0.4);
	}
</style>

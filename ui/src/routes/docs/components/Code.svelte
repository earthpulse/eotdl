<script>
	import ContentCopy from "svelte-material-icons/ContentCopy.svelte";
	import { fade } from "svelte/transition";

	let { lang = "bash", children } = $props();

	let visible = $state(false);
	let clicked = $state(false);
	let ref = $state(null);
</script>

<div
	class="relative w-full"
	onmouseenter={() => (visible = true)}
	onmouseleave={() => (visible = false)}
	role="region"
>
	<pre class="language-{lang}"><code bind:this={ref}
			>{@render children()}</code
		></pre>
	{#if visible}
		<button
			transition:fade={{ duration: 200 }}
			class="absolute top-2 right-2 bg-white hover:cursor-pointer rounded-lg p-2 active:transform active:scale-95"
			onclick={() => {
				const el = document.createElement("textarea");
				el.value = ref.innerText;
				document.body.appendChild(el);
				el.select();
				document.execCommand("copy");
				document.body.removeChild(el);
				clicked = true;
			}}
		>
			<ContentCopy size="15" />
		</button>
	{/if}
</div>

<!-- <style>
	pre {
		width: inherit;
		max-width: calc(100vw - 400px);
	}
</style> -->

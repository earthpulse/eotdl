<script>
	import ContentCopy from "svelte-material-icons/ContentCopy.svelte";
	import { fade } from "svelte/transition";

	export let lang = "bash";
	let visible = false;
	let clicked = false;
	let ref = null;
</script>

<div
	class="relative w-full"
	on:mouseenter={() => (visible = true)}
	on:mouseleave={() => (visible = false)}
>
	<pre class="language-{lang}"><code bind:this={ref}><slot /></code></pre>
	{#if visible}
		<button
			transition:fade={{ duration: 200 }}
			class="absolute top-2 right-2 bg-white hover:cursor-pointer rounded-lg p-2 active:transform active:scale-95"
			on:click={() => {
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

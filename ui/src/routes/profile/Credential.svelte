<script>
	let { value = "lkjansfo9pansws34nfqp80w383" } = $props();
	import { fade } from "svelte/transition";

	let message = $state(null);

	const copyToClipboard = (text) => {
		navigator.clipboard.writeText(value);
		console.log("copied to clipboard");
		message = "Copied!";
		setTimeout(() => {
			message = null;
		}, 500);
	};

	const format = (text) => {
		if (!text || text.length < 10) return text;
		return text.slice(0, 10) + "****";
	};
</script>

<button onclick={copyToClipboard} class="hover:underline"
	>{format(value)}</button
>
{#if message}
	<span class="text-sm text-gray-400" in:fade out:fade>{message}</span>
{/if}

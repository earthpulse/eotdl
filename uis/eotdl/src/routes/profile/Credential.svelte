<script>
	export let value = "lkjansfo9pansws34nfqp80w383";

	const copyToClipboard = (text) => {
		navigator.clipboard.writeText(value);
		console.log("copied to clipboard");
	};

	const format = (text) => {
		return text.slice(0, 5) + "****";
	};
</script>

<button on:click={copyToClipboard}>{format(value)}</button>

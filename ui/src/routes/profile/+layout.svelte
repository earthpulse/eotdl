<script>
	import ProfileNavBar from "./ProfileNavBar.svelte";
</script>

<div
	class="w-full flex flex-col items-left sm:px-14 px-3 min-h-screen max-w-5xl m-auto"
>
	<div class="py-10 mt-10 flex sm:flex-row flex-col gap-12">
		<ProfileNavBar />
		<slot />
	</div>
</div>

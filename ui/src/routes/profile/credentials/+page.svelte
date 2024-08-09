<script>
    import ProfileNavBar from "../ProfileNavBar.svelte";
	import Credentials from "../Credentials.svelte";
	export let data;

</script>

<div class="w-full flex flex-col items-left sm:px-14 px-3 h-fit">
    <div class="py-10 mt-10 flex sm:flex-row  flex-col">
        <ProfileNavBar />
        <div class="px-3 w-full max-w-6xl flex flex-col gap-3">
            <h1 class="sm:text-left text-center w-full text-2xl">Credentials</h1>
			<Credentials {data} />
		</div>
    </div>
</div>
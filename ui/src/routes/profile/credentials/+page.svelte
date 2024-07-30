<script>
    import ProfileNavBar from "../ProfileNavBar.svelte";
    import updateProfile from "$lib/auth/updateProfile";
	import TermsAndConditions from "../TermsAndConditions.svelte";
	import Credentials from "../Credentials.svelte";
	export let data;

	let newName;
	let loading;
	const edit = async () => {
		loading = true;
		try {
			await updateProfile(newName, data.id_token);
			document.getElementById("edit-profile").checked = false;
			data.user.name = newName;
		} catch (e) {
			alert(e.message);
		}
		loading = false;
	};
</script>

<div class="w-full flex flex-col items-left pl-14 h-fit">
    <div class="py-10 mt-10 flex">
        <ProfileNavBar />
        <div class="px-3 w-full max-w-6xl flex flex-col gap-3">
            <h1 class="text-left w-full text-2xl">Credentials</h1>
			<Credentials {data} />
		</div>
    </div>
</div>
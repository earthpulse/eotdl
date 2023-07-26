<script>
	import updateProfile from "$lib/auth/updateProfile";
	import TermsAndConditions from "./TermsAndConditions.svelte";

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

<svelte:head>
	<title>EOTDL | Profile</title>
	<meta name="description" content="user profile" />
</svelte:head>

<div class="w-full flex flex-col items-center">
	<div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-3">
		<h1 class="text-left w-full text-2xl">Profile</h1>
		<div class="flex flex-row w-full gap-3">
			<div class="avatar">
				<div class="w-32 rounded-full">
					<img
						src={data?.user?.picture || "/avatar.webp"}
						alt="avatar"
					/>
				</div>
			</div>
			<div>
				<h2 class="text-2xl">{data?.user?.name}</h2>
				<h3 class="text-xl">Email: {data?.user?.email}</h3>
				<label
					for="edit-profile"
					class="text-gray-400 cursor-pointer hover:underline"
					>Edit</label
				>
			</div>
		</div>
		<TermsAndConditions />
	</div>
</div>

<input type="checkbox" id="edit-profile" class="modal-toggle" />
<label for="edit-profile" class="modal cursor-pointer">
	<label class="modal-box relative" for="">
		<form on:submit|preventDefault={edit} class="flex flex-col gap-2">
			<h3 class="text-lg font-bold">Edit profile</h3>
			<span>
				<p>Name</p>
				<input
					class="input input-bordered w-full"
					type="text"
					placeholder={data?.user?.name}
					bind:value={newName}
				/>
				<p class="text-sm text-gray-400">*Name should be unique</p>
			</span>
			<span class="self-end">
				<label
					for="edit-profile"
					class="btn btn-ghost btn-outline btn-error">Close</label
				>
				<button
					class="btn btn-ghost btn-outline {loading && 'loading'}"
					type="submit">Update</button
				>
			</span>
		</form>
	</label>
</label>

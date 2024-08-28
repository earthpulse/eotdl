<script>
    import { page } from "$app/stores";
    let profileSections = {
        Profile: "/profile",
        Credentials: "/profile/credentials",
        "Api keys": "/profile/apikeys",
    };
</script>

<div class="items-center text-sm">
    <ul class="flex sm:flex-col flex-row gap-4">
        {#each Object.keys(profileSections) as section}
            <li
                class="w-full py-[1px] hover:border-slate-500 border-b-[2px] {$page
                    .url.pathname == profileSections[section]
                    ? ' border-black border-b-[2px] '
                    : ''} text-slate-500 hover:text-slate-900"
            >
                <a href={profileSections[section]}>
                    {section}
                </a>
            </li>
        {/each}
    </ul>
</div>

<slot />

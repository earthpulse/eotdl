<script>
    import { page } from "$app/stores"
    let profileSections = {
        "Profile":"/profile",
        "Credentials":"/profile/credentials",
        "Api keys": "/profile/apikeys",
    }
</script>
<div class="px-6 py-6 items-center">
    <ul class="flex sm:flex-col flex-row gap-4">
        {#each Object.keys(profileSections) as section }
            <li class="w-full py-[1px] hover:border-slate-500 border-b-[2px] {$page.url.pathname == profileSections[section] ? " border-black border-b-[2px] ": ""}">
                <a class="font-semibold text-lg" href="{profileSections[section]}">
                    {section}
                </a>
            </li>
        {/each}
    </ul>
</div>

<slot />
<script>
    import { page } from "$app/stores"
    let profileSections = {
        "Profile":$page.url.pathname == "profile" ? $page.url.pathname : "/profile",
        "Credentials":$page.url.pathname.includes("credentials") ? $page.url.pathname : "/profile/credentials",
        "Api keys":$page.url.pathname.includes("apikeys") ? $page.url.pathname : "/profile/apikeys",
    }
</script>
<div class="pr-6 h-full">
    <ul class="flex flex-col gap-4">
        {#each Object.keys(profileSections) as section }
            <li class="w-full py-[1px] hover:border-slate-500 border-b-[2px] {$page.url.pathname == profileSections[section] ? " border-black border-b-[2px] ": ""}">
                <a class="font-semibold text-lg" href="{profileSections[section]}">
                    {section}
                </a>
            </li>
        {/each}
    </ul>
</div>
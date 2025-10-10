<script>
    import auth from "$stores/auth.svelte";
    import { page } from "$app/stores";
    import HomeOutline from "svelte-material-icons/HomeOutline.svelte";
    import DatabaseOutline from "svelte-material-icons/DatabaseOutline.svelte";
    import TextBoxMultipleOutline from "svelte-material-icons/TextBoxMultipleOutline.svelte";
    import CogOutline from "svelte-material-icons/CogOutline.svelte";
    import CloudCogOutline from "svelte-material-icons/CloudCogOutline.svelte";
    import ChartBoxPlusOutline from "svelte-material-icons/ChartBoxPlusOutline.svelte";
    import SchoolOutline from "svelte-material-icons/SchoolOutline.svelte";
    import notifications from "$stores/notifications.svelte";

    let { loading } = $props();

    const links = [
        { href: "/", label: "Home", icon: HomeOutline },
        { href: "/datasets", label: "Datasets", icon: DatabaseOutline },
        { href: "/models", label: "Models", icon: ChartBoxPlusOutline },
        { href: "/pipelines", label: "Pipelines", icon: ChartBoxPlusOutline },
        {
            href: "https://hub.api.eotdl.com/",
            label: "Workspace",
            icon: CloudCogOutline,
        },
        { href: "/tutorials", label: "Tutorials", icon: SchoolOutline },
        { href: "/applications", label: "Applications", icon: CogOutline },
        { href: "/docs", label: "Docs", icon: TextBoxMultipleOutline },
    ];
    const secondary_links = [
        // { href: "/", label: "Labelling" },
        // { href: "/", label: "Training" },
        { href: "/blog", label: "Blog" },
        // { href: "/", label: "Youtube" },
    ];
    const external_links = [
        // { href: "/", label: "Youtube" },
        { href: "https://discord.gg/hYxc5AJB92", label: "Discord" },
        { href: "https://github.com/earthpulse/eotdl", label: "Github" },
        { href: "https://platform.ai4eo.eu/", label: "AI4EO" },
    ];

    let notificationCount = $derived(notifications.data?.length || 0);
</script>

<div class="grid place-items-center w-full">
    <ul
        class="flex flex-row gap-6 w-full justify-end max-w-7xl p-3 text-blue-500 items-center uppercase"
    >
        {#each links as link}
            <li class="hidden lg:block text-slate-500 gap-2 text-sm">
                <a
                    href={link.href}
                    class="{$page.url.pathname == '/'
                        ? 'text-slate-300 hover:text-white'
                        : 'text-slate-600 hover:text-slate-800'} hover:underline flex floex-row gap-1 items-center"
                >
                    <link.icon class="h-4 w-4" />
                    {link.label}
                </a>
            </li>
        {/each}
        <li>
            {#if auth.user}
                <a
                    href={loading ? "" : "/api/auth/logout"}
                    class="border-2 rounded-md px-2 hover:border-gray-300 {$page
                        .url.pathname == '/'
                        ? 'text-slate-300 hover:text-white hover:border-white border-slate-400'
                        : 'text-slate-600 hover:text-slate-800 border-slate-400 hover:border-slate-600'}"
                    >Sign Out</a
                >
            {:else}
                <a
                    href={loading ? "" : "/api/auth/login"}
                    class="border-2 rounded-md px-2 hover:border-gray-300 {$page
                        .url.pathname == '/'
                        ? 'text-gray-300 hover:text-white hover:border-white border-slate-400'
                        : 'text-slate-600 hover:text-slate-800 border-slate-400 hover:border-slate-600'}"
                    >Sign In</a
                >
            {/if}
        </li>
        <li>
            <a href={auth.user ? "/profile" : ""}>
                <div
                    class={auth.user ? "tooltip tooltip-bottom" : ""}
                    data-tip={auth.user ? "Profile" : "Profile"}
                >
                    <div class="avatar indicator">
                        {#if notificationCount > 0}
                            <span class="indicator-item badge badge-secondary"
                                >{notificationCount}</span
                            >
                        {/if}
                        <div class="w-10 rounded-full">
                            <img
                                src={auth.user?.picture || "/avatar.webp"}
                                alt="avatar"
                            />
                        </div>
                    </div>
                </div>
            </a>
        </li>
        <!-- {#if auth.user}
            <li class="flex-row gap-2 items-center flex {$page.url.pathname == '/'
                            ? 'text-slate-300 hover:text-white'
                            : 'text-slate-600 hover:text-slate-800'}">
                <img src="/gamification/gold_coin_pile.png" alt="logo" class="h-8" />
                <p>{auth.user.credits}</p>
                <img src="/gamification/silver_coin_pile.png" alt="logo" class="h-8" />
                <p>{auth.user.pseudocredits}</p>
            </li>
        {/if} -->
        <button tabindex="0" class="dropdown dropdown-end cursor-pointer">
            <div>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke={$page.url.pathname == "/" ? "white" : "black"}
                    ><path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 6h16M4 12h16M4 18h7"
                    /></svg
                >
            </div>
            <ul
                class="px-7 text-black dropdown-content border py-4 flex flex-col gap-2 rounded mt-4 text-sm bg-slate-100"
            >
                {#each links as link}
                    <li class="lg:hidden block">
                        <a href={link.href} class="hover:underline"
                            >{link.label}</a
                        >
                    </li>
                {/each}
                {#each secondary_links as link}
                    <li>
                        <a href={link.href} class="hover:underline"
                            >{link.label}</a
                        >
                    </li>
                {/each}
                {#each external_links as link}
                    <li>
                        <a
                            href={link.href}
                            class="hover:underline"
                            target="_blank"
                            rel="noopener noreferrer">{link.label}</a
                        >
                    </li>
                {/each}
            </ul>
        </button>
    </ul>
</div>

<!-- <div class="grid place-items-center w-full">
    <ul
        class="flex flex-row gap-6 w-full justify-end max-w-6xl p-3 text-blue-500 items-center uppercase"
    >
        {#each links as link}
            <li
                class="hidden font-bold lg:flex
                {$page.url.pathname == '/'
                    ? 'text-gray-300 hover:text-white'
                    : 'text-slate-600 hover:text-slate-800'} 
                gap-1 text-[15px] items-center"
            >
                <svelte:component this={link.icon} />
                <a
                    href={link.href}
                    class="hover:underline flex flex-row gap-1 items-center"
                >
                    {link.label}
                </a>
            </li>
        {/each}
    </ul>

    <li>
        {#if $user}
            <a
                href={loading ? "" : "/api/auth/logout"}
                class="border-2 {$page.url.pathname == '/'
                    ? 'text-gray-300 hover:border-white border-slate-400'
                    : 'text-slate-600 border-slate-400 hover:border-slate-800'} rounded-md px-2"
                >Sign Out</a
            >
        {:else}
            <a
                href={loading ? "" : "/api/auth/login"}
                class="border-2 {$page.url.pathname == '/'
                    ? 'text-gray-300 hover:border-white border-slate-400'
                    : 'text-slate-600 border-slate-400 hover:border-slate-800'} rounded-md px-2"
                >Sign In</a
            >
        {/if}
    </li>
    <li>
        {#if $user}
            <a href={$user ? "/profile" : ""}>
                <div
                    class={$user ? "tooltip tooltip-bottom" : ""}
                    data-tip={$user ? "Profile" : "Profile"}
                >
                    <div class="avatar">
                        <div class="w-10 rounded-full">
                            <img
                                src={$user?.picture || "/avatar.webp"}
                                alt="avatar"
                            />
                        </div>
                    </div>
                </div>
            </a>
        {/if}
    </li>
    <button tabindex="0" class="dropdown dropdown-end cursor-pointer">
        <div>
            <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-7 w-7"
                fill="none"
                viewBox="0 0 24 24"
                stroke={$page.url.pathname == "/" ? "white" : "black"}
                ><path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="1"
                    d="M 4 6 h 16 M 4 12 h 16 M 4 18 h 16"
                /></svg
            >
        </div>
        <ul
            class="px-7 text-black dropdown-content border py-4 flex flex-col gap-2 rounded mt-4 text-sm bg-slate-100"
        >
            {#each links as link}
                <li class="lg:hidden block">
                    <a href={link.href} class="hover:underline">{link.label}</a>
                </li>
            {/each}
            {#each secondary_links as link}
                <li>
                    <a href={link.href} class="hover:underline">{link.label}</a>
                </li>
            {/each}
            {#each external_links as link}
                <li>
                    <a
                        href={link.href}
                        class="hover:underline"
                        target="_blank"
                        rel="noopener noreferrer">{link.label}</a
                    >
                </li>
            {/each}
        </ul>
    </button>
</div> -->

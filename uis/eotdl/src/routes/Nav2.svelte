<script>
    import { user } from "$stores/auth";
    export let loading;

    const links = [
        { href: "/", label: "Home" },
        { href: "/datasets", label: "Datasets" },
        // { href: "/models", label: "Models" },
        { href: "/docs", label: "Docs" },
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
</script>

<div class="grid place-items-center w-full">
    <div class="w-full p-3 bg-red-400 grid items-center">
        <p class="m-auto max-w-6xl">
            Meet us at the upcoming
            <a
                class="text-white hover:underline"
                href="https://www.bigdatafromspace2023.org"
                target="_blank"
                rel="noopener noreferrer">BiDS'23</a
            >
            event, that will take place on 6-9 November 2023 in Vienna, Austria.
            A <span class="underline">hands-on tutorial session </span>on EOTDL
            will take place on November 6th from 9:00 to 12:30, and everyone is
            welcome to join! More information
            <a
                class="text-white hover:underline"
                href="https://www.bigdatafromspace2023.org/satellite-events"
                target="_blank"
                rel="noopener noreferrer">here</a
            >.
        </p>
    </div>
    <ul
        class="flex flex-row gap-6 w-full justify-end max-w-6xl p-3 text-blue-500 items-center uppercase"
    >
        {#each links as link}
            <li class="hidden sm:block">
                <a href={link.href} class="hover:underline">{link.label}</a>
            </li>
        {/each}
        <li>
            {#if $user}
                <a
                    href={loading ? "" : "/api/auth/logout"}
                    class="border-2 rounded-md px-2 hover:border-gray-300"
                    >Sign Out</a
                >
            {:else}
                <a
                    href={loading ? "" : "/api/auth/login"}
                    class="border-2 rounded-md px-2 hover:border-gray-300"
                    >Sign In</a
                >
            {/if}
        </li>
        <li>
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
        </li>
        <button tabindex="0" class="dropdown dropdown-end cursor-pointer">
            <div>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
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
                    <li class="sm:hidden block">
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

<script>
  import { navigating } from "$app/stores";
  let ref = null;
  let clicked = false;
  $: if ($navigating) {
    if (clicked) ref.click();
    clicked = false;
  }
  let website_links = [
    {
      name: "Datasets",
      link: "/",
    },
    {
      name: "Models",
      link: "/",
    },
    {
      name: "Labelling",
      link: "/",
    },
    {
      name: "Training",
      link: "/",
    },
  ];
  let reference_links = [
    {
      name: "Docs",
      link: "/docs",
    },
    {
      name: "Blog",
      link: "/",
    },
    {
      name: "Github",
      link: "https://github.com/earthpulse/eotdl",
    },
    {
      name: "Youtube",
      link: "/",
    },
  ];
  let community_links = [
    {
      name: "Discord",
      link: "/",
    },
    {
      name: "Twitter",
      link: "/",
    },
  ];
</script>

<div class="drawer drawer-end">
  <input id="my-drawer-3" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col">
    <!-- Navbar -->
    <div
      class="w-full navbar bg-primary text-base-100 sticky top-0 left-0 z-[999] flex flex-row align-center justify-center"
    >
      <div class="w-full max-w-6xl flex flex-row justify-between">
        <div class="px-2 mx-2">
          <a class="link link-hover text-xl" href="/">EO-TDL</a>
        </div>
        <div class="md:hidden justify-end" on:click={() => (clicked = true)}>
          <label for="my-drawer-3" class="btn btn-square btn-ghost">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              class="inline-block w-6 h-6 stroke-current"
              ><path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              /></svg
            >
          </label>
        </div>
        <div class="hidden md:block">
          <ul class="menu menu-horizontal">
            <!-- Navbar menu content here -->
            <li><a class="link link-hover" href="/">Datasets</a></li>
            <li><a class="link link-hover" href="/">Models</a></li>
            <li><a class="link link-hover" href="/docs">Docs</a></li>
            <li>
              <a
                class="link link-hover"
                href="https://platform.ai4eo.eu/"
                target="_blank">AI4EO )</a
              >
            </li>
            <li tabindex="0" class="dropdown dropdown-end cursor-pointer">
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
                class="px-7 text-black bg-base-100 dropdown-content border py-4 flex flex-col gap-2 rounded mt-2 text-sm"
              >
                <li><a class="link link-hover" href="/">Labelling</a></li>
                <li><a class="link link-hover" href="/">Training</a></li>
                <li><a class="link link-hover" href="/">Blog</a></li>
                <li><a class="link link-hover" href="/">Youtube</a></li>
                <li><a class="link link-hover" href="/">Discord</a></li>
                <li>
                  <a
                    class="link link-hover"
                    href="https://github.com/earthpulse/eotdl"
                    target="_blank">Github</a
                  >
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <slot />
  </div>
  <div class="drawer-side">
    <label for="my-drawer-3" class="drawer-overlay" bind:this={ref} />
    <div class="p-4 overflow-y-auto w-80 bg-base-100">
      <!-- Sidebar content here -->
      <div
        class="badge badge-success mb-2 text-sm w-full font-bold text-green-700"
      >
        Website
      </div>
      <ul class="w-full grid grid-cols-2 center items-center gap-2 ">
        {#each website_links as { name, link }}
          <li
            class="w-full grid items-center border rounded-md hover:bg-base-200 text-sm"
          >
            <a class="text-center" href={link}>{name}</a>
          </li>
        {/each}
      </ul>
      <div
        class="badge badge-warning mb-2 text-sm w-full mt-6 font-bold text-yellow-700"
      >
        Reference
      </div>
      <ul class="w-full grid grid-cols-2 center items-center gap-2 ">
        {#each reference_links as { name, link }}
          <li
            class="w-full grid items-center border rounded-md hover:bg-base-200 text-sm"
          >
            <a class="text-center" href={link}>{name}</a>
          </li>
        {/each}
      </ul>
      <div
        class="badge badge-error mb-2 text-sm w-full mt-6 text-red-900 font-bold"
      >
        Community
      </div>
      <ul class="w-full grid grid-cols-2 center items-center gap-2 ">
        {#each community_links as { name, link }}
          <li
            class="w-full grid items-center border rounded-md hover:bg-base-200 text-sm"
          >
            <a class="text-center" href={link}>{name}</a>
          </li>
        {/each}
      </ul>
    </div>
  </div>
</div>

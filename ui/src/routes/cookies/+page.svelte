<script>
    import { onMount } from "svelte";
    let ref = null;

    onMount(() => {
        const script = document.createElement("script");
        script.id = "CookieDeclaration";
        script.async = true;
        script.src =
            "https://consent.cookiebot.com/1c333f40-58bf-4d3b-9a10-d57b72c9176a/cd.js";
        script.type = "text/javascript";
        ref.appendChild(script);
    });
</script>

<div class="w-full flex flex-col items-center pt-20 max-w-6xl m-auto">
    <div bind:this={ref} />
</div>

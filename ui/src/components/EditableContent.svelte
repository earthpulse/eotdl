<script>
    import { Carta, MarkdownEditor } from "carta-md";
    import "carta-md/default.css";
    import "$styles/carta-md.css";
    import { browser } from "$app/environment";

    // Added polyfill for global variable in the browser environment.
    if (browser && typeof global === "undefined") {
        window.global = window;
    }

    let DOMPurify;

    const loadDOMPurify = async () => {
        DOMPurify = await import("isomorphic-dompurify");
    };

    $: if (browser) {
        loadDOMPurify();
    }

    const carta = new Carta({
        extensions: [],
        sanitizer: DOMPurify?.sanitize,
    });

    let content = null;
    export let edit = false;
    export let value;

    $: if (carta && value) {
        carta.render(value).then((rendered) => {
            content = rendered;
        });
    }

    let html = null;

    const renderHtml = async () => {
        html = await carta.render(value);
    };
</script>

{#if edit && carta}
    <div class="flex justify-center">
        <div
            on:change={renderHtml}
            class="w-full flex flex-col items-center justify-center p-2 rounded-xl"
        >
            <MarkdownEditor {carta} bind:value />
        </div>
    </div>
{:else}
    <div class="content">
        {@html content}
    </div>
{/if}

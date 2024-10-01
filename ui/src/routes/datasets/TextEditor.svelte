<script>
  import { Carta, MarkdownEditor } from "carta-md";
  import "carta-md/default.css"; /* Default theme */
  import "$styles/carta-md.css";
  import DOMPurify from "isomorphic-dompurify";
  import { browser } from "$app/environment";

  let x;
  let sm;

  $: if (browser) {
    x = window?.matchMedia("(max-width: 640px)");
    let sm = x.matches ? true : false;
    let normal = x.matches ? false : true;
    // Attach listener function on state changes
    x.addEventListener("change", function () {
      if (x.matches) {
        sm = true;
        normal = false;
      } else {
        sm = false;
        normal = true;
      }
    });
  }

  const carta = new Carta({
    extensions: [],
    sanitizer: DOMPurify.sanitize,
  });

  export let value;

  let html = null;

  const renderHtml = async () => {
    html = await carta.render(value);
  };
</script>

<div class="flex justify-center">
  <div
    on:change={renderHtml}
    class="w-[62rem] flex flex-col items-center justify-center p-2 rounded-xl"
  >
    <MarkdownEditor mode={sm ? "tabs" : "split"} {carta} bind:value />
  </div>
</div>

<slot />

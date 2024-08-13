<script>
	import { Carta, MarkdownEditor } from 'carta-md';
	import 'carta-md/default.css'; /* Default theme */
	import "$styles/carta-md.css"
  import DOMPurify from 'isomorphic-dompurify';

  import TurndownService from 'turndown';
  const carta = new Carta({
		extensions: [],
    sanitizer: DOMPurify.sanitize
	});

  export let content;
  var turndownService = new TurndownService({codeBlockStyle:"fenced", preformattedCode:true})
	let value = turndownService.turndown(content);
  const rebuildHtml = async () => {
    content = await carta.render(value);
  }
</script>

<div class="flex justify-center">
    <div on:change={rebuildHtml} class="w-[62rem] flex flex-col items-center justify-center p-2 rounded-xl">
        <MarkdownEditor mode="split" {carta} bind:value />
    </div>
</div>
<slot />

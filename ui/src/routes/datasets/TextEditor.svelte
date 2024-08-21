<script>
	import { Carta, MarkdownEditor } from 'carta-md';
	import 'carta-md/default.css'; /* Default theme */
	import "$styles/carta-md.css"
  import DOMPurify from 'isomorphic-dompurify';
  import TurndownService from 'turndown';
  import {tables} from "turndown-plugin-gfm";
  var x = window.matchMedia("(max-width: 640px)")
  let sm = x.matches ? true : false;
  let normal = x.matches ? false : true;;
  // Attach listener function on state changes
  x.addEventListener("change", function() {
    if(x.matches){
      sm = true;
      normal = false;
    }
    else{
      sm = false;
      normal = true;
    }
  });

  const carta = new Carta({
		extensions: [],
    sanitizer: DOMPurify.sanitize
	});

  export let content;
  var turndownService = new TurndownService({codeBlockStyle:"fenced", preformattedCode:true})
  turndownService.use(tables);
  let value = turndownService.turndown(content);
  const renderHtml = async () => {
    content = await carta.render(value);
  }
</script>

<div class="flex justify-center">
    <div on:change={renderHtml} class="w-[62rem] flex flex-col items-center justify-center p-2 rounded-xl">
        <MarkdownEditor mode={sm ? "tabs" : "split"} {carta} bind:value />
    </div>
</div>
<slot />

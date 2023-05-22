<script>
  import "../../styles/quill.snow.css";
  import { onMount } from "svelte";
  // import Quill from "quill";

  export let options = {
    placeholder: "Description...",
    modules: {
      toolbar: [
        [{ header: [1, 2, 3, false] }],
        ["bold", "italic", "underline", "strike"],
        ["link", "code-block"],
      ],
    },
    theme: "snow",
  };
  export let content = "";

  let a = "";

  let quillInstance;
  onMount(async () => {
    const Quill = (await import("quill")).default;
    if (quillInstance) return;
    const node = document.getElementById("editor");
    quillInstance = new Quill(node, options);
    const container = node.getElementsByClassName("ql-editor")[0];
    if (content) container.innerHTML = content;
    quillInstance.on("text-change", (delta, oldDelta, source) => {
      content = container.innerHTML;
    });
  });
</script>

<div id="editor" />

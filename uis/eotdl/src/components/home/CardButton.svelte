<script>
  export let variant = "primary";

  let _class = "btn hover:drop-shadow-xl hover:scale-110";
  if (variant === "secondary") {
    _class +=
      " btn-ghost btn-outline border-base-300 hover:bg-transparent hover:border-base-300 hover:text-black";
  } else {
    _class += " btn-primary hover:bg-primary hover:border-primary";
  }
</script>

<button class={_class}>
  <slot />
</button>

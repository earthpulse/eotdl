<script>
  import "../styles/app.css";
  import Nav from "./Nav.svelte";
  import Nav2 from "./Nav2.svelte";
  import Footer from "./Footer.svelte";
  import { user, id_token } from "$stores/auth";

  export let data;

  user.set(data?.user);
  id_token.set(data?.id_token);
</script>

<main class="min-h-screen flex flex-col items-center justify-between">
  <div class="w-full">
    <Nav />
    <div class="relative">
      <slot />
      <div class="absolute top-0 left-0 w-full">
        <Nav2 />
      </div>
    </div>
  </div>
  <Footer />
</main>

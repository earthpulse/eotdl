<script>
  import "../app.css";
  import Nav from "../components/layout/Nav.svelte";
  import Nav2 from "../components/layout/Nav2.svelte";
  import Footer from "../components/layout/Footer.svelte";
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
      <div class="absolute top-0 left-0 w-full"><Nav2 user={data.user} /></div>
    </div>
  </div>
  <Footer />
</main>

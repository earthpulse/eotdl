<script>
  import "../styles/app.css";
  import Nav from "./Nav.svelte";
  import Nav2 from "./Nav2.svelte";
  import Footer from "./Footer.svelte";
  import { user, id_token } from "$stores/auth";
  import { browser } from "$app/environment";

  export let data;
  let loading = !data?.user;

  user.set(data?.user);
  id_token.set(data?.id_token);

  const me = async () => {
    const res = await fetch("/api/auth/me");
    if (res.status != 200) {
      loading = false;
      return;
    }
    const data = await res.json();
    user.set(data);
    loading = false;
  };

  // prerendered routes won't call hooks.server.js so the user info will not be retrieved
  // check if id_token in cookies and fetch user info if so
  $: if (browser && !data?.user) me();
</script>

<main class="min-h-screen flex flex-col items-center justify-between">
  <div class="w-full">
    <Nav />
    <div class="relative">
      <slot />
      <div class="absolute top-0 left-0 w-full">
        <Nav2 {loading} />
      </div>
    </div>
  </div>
  <Footer />
</main>

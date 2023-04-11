<script>
<<<<<<< HEAD
  import "../app.css";
  import Nav from "../components/layout/Nav.svelte";
  import Footer from "../components/layout/Footer.svelte";
=======
  import "../styles/app.css";
  import Nav from "./Nav.svelte";
  import Nav2 from "./Nav2.svelte";
  import Footer from "./Footer.svelte";
  import { user, id_token } from "$stores/auth";

  export let data;

  user.set(data?.user);
  id_token.set(data?.id_token);
>>>>>>> develop
</script>

<Nav>
  <main class="min-h-screen flex flex-col items-center justify-between">
    <slot />
    <Footer />
  </main>
</Nav>

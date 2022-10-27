<script>
  import "../app.css";

  import Nav from "../components/layout/Nav.svelte";
  import Footer from "../components/layout/Footer.svelte";
</script>

<Nav>
  <main class="min-h-screen flex flex-col items-center justify-between">
    <slot />
    <Footer />
  </main>
</Nav>

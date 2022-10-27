<script>
  import Hero from "../components/layout/home/Hero.svelte";
  import Cards from "../components/layout/home/Cards.svelte";
  import Consortium from "../components/layout/home/Consortium.svelte";
</script>

<svelte:head>
  <title>EO-TDL | Home</title>
</svelte:head>

<div class="w-full flex flex-col items-center">
  <Hero />
  <Cards />
  <Consortium />
</div>

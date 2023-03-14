<script>
  import Hero from "../components/home/Hero.svelte";
  import Consortium from "../components/home/Consortium.svelte";
  import Recent from "../components/home/Recent.svelte";
  import Popular from "../components/home/Popular.svelte";
  import Contributors from "../components/home/Contributors.svelte";
  import Posts from "../components/home/Posts.svelte";

  // export let data; // user data coming from layout
</script>

<svelte:head>
  <title>EO-TDL | Home</title>
</svelte:head>

<div class="w-full flex flex-col items-center">
  <Hero />
  <!-- <Recent />
  <Popular />
  <Contributors />
  <Posts /> -->
  <Consortium />
</div>

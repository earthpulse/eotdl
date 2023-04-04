<script>
  import Hero from "./Hero.svelte";
  import Consortium from "./Consortium.svelte";
  import Recent from "./Recent.svelte";
  import Popular from "./Popular.svelte";
  import Posts from "./Posts.svelte";
  import Leaderboard from "./datasets/Leaderboard.svelte";

  export let data;
</script>

<svelte:head>
  <title>EO-TDL | Home</title>
</svelte:head>

<div class="w-full flex flex-col items-center">
  <Hero />
  <Recent {data} />
  <Popular {data} />
  <div class="mt-[100px] w-full">
    <Leaderboard leaderboard={data.leaderboard} />
  </div>
  <!--<Posts /> -->
  <Consortium />
</div>

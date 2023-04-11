<script>
<<<<<<< HEAD
  import Hero from "../components/layout/home/Hero.svelte";
  import Cards from "../components/layout/home/Cards.svelte";
  import Consortium from "../components/layout/home/Consortium.svelte";
=======
  import Hero from "./Hero.svelte";
  import Consortium from "./Consortium.svelte";
  import Recent from "./Recent.svelte";
  import Popular from "./Popular.svelte";
  import Posts from "./Posts.svelte";
  import Leaderboard from "./datasets/Leaderboard.svelte";

  export let data;
>>>>>>> develop
</script>

<svelte:head>
  <title>EOTDL | Home</title>
</svelte:head>

<div class="w-full flex flex-col items-center">
  <Hero />
<<<<<<< HEAD
  <Cards />
=======
  <Recent {data} />
  <Popular {data} />
  <div class="mt-[100px] w-full">
    <Leaderboard leaderboard={data.leaderboard} />
  </div>
  <Posts posts={data.posts} />
>>>>>>> develop
  <Consortium />
</div>

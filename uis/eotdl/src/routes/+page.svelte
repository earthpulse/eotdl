<script>
  import Hero from "./Hero.svelte";
  import Consortium from "./Consortium.svelte";
  import Recent from "./Recent.svelte";
  import Popular from "./Popular.svelte";
  import Posts from "./Posts.svelte";
  import Leaderboard from "./datasets/Leaderboard.svelte";
  import { browser } from "$app/environment";
  import retrieveDatasets from "../lib/datasets/retrieveDatasets";
  import retrieveDatasetsLeaderboard from "../lib/datasets/retrieveDatasetsLeaderboard";
  import retrievePopularDatasets from "../lib/datasets/retrievePopularDatasets";

  let datasets, leaderboard, popular_datasets;
  const load = async () => {
    datasets = await retrieveDatasets(fetch, 3);
    leaderboard = await retrieveDatasetsLeaderboard(fetch);
    popular_datasets = await retrievePopularDatasets(fetch, 3);
  };

  $: if (browser) load();

  export let data;
</script>

<svelte:head>
  <title>EOTDL | Home</title>
  <meta
    name="description"
    content="EOTDL is a platform for sharing and discovering training datasets."
  />
</svelte:head>

<div class="w-full flex flex-col items-center">
  <Hero />
  <Recent {datasets} />
  <Popular datasets={popular_datasets} />
  <div class="mt-[100px] w-full">
    <Leaderboard {leaderboard} />
  </div>
  <Posts posts={data.posts} />
  <Consortium />
</div>

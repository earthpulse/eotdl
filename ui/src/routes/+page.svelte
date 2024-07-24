<script>
  import HeroBackgorund from "./HeroBackgorund.svelte";
  import Hero from "./Hero.svelte";
  import Consortium from "./Consortium.svelte";
  import RecentDatasets from "./RecentDatasets.svelte";
  import PopularDatasets from "./PopularDatasets.svelte";
  import DatasetsLeaderboard from "./DatasetsLeaderboard.svelte";
  import RecentModels from "./RecentModels.svelte";
  import PopularModels from "./PopularModels.svelte";
  import ModelsLeaderboard from "./ModelsLeaderboard.svelte";
  import Posts from "./Posts.svelte";

  export let data;
</script>

<svelte:head>
  <title>EOTDL | Home</title>
  <meta
    name="description"
    content="EOTDL is a platform for sharing and discovering training Models."
  />
</svelte:head>

<div class="w-full flex flex-col items-center">
  <HeroBackgorund/>
  <Hero />
  <RecentDatasets />
  <PopularDatasets />
  <DatasetsLeaderboard />
  <div class="mt-[100px]" />
  <RecentModels />
  <PopularModels />
  <ModelsLeaderboard />
  <Posts posts={data.posts} />
  <Consortium />
</div>

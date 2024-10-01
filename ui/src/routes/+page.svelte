<script>
  import HeroBackground from "./HeroBackground.svelte";
  import Hero from "./Hero.svelte";
  import Consortium from "./Consortium.svelte";
  import RecentDatasets from "./RecentDatasets.svelte";
  import PopularDatasets from "./PopularDatasets.svelte";
  import DatasetsLeaderboard from "./DatasetsLeaderboard.svelte";
  import RecentModels from "./RecentModels.svelte";
  import PopularModels from "./PopularModels.svelte";
  import ModelsLeaderboard from "./ModelsLeaderboard.svelte";
  import Posts from "./Posts.svelte";
  import { tutorials } from "./tutorials/tutorials";
  import HomeTutorials from "./HomeTutorials.svelte";
  import Events from "./Events.svelte";
  export let data;
</script>

<svelte:head>
  <title>EOTDL | Home</title>
  <meta
    name="description"
    content="EOTDL is a platform for sharing and discovering training Datasets and Models for Earth Observation applications."
  />
</svelte:head>

<div class="w-full flex flex-col items-center">
  <!-- <HeroBackground /> -->
  <Hero />
  <div
    class="w-full max-w-6xl"
    style="background: url('backgrounds/Group-1170.png') center center/cover"
  >
    <div class="flex flex-col-reverse md:flex-row">
      <div class="w-full md:flex-grow">
        <HomeTutorials {tutorials} />
        <RecentDatasets tags={data.tags} />
        <PopularDatasets tags={data.tags} />
        <DatasetsLeaderboard />
      </div>
      <div class="w-full md:w-[300px] p-4">
        <div class="h-full flex justify-center">
          <Events />
        </div>
      </div>
    </div>
  </div>
  <div
    class="w-full"
    style="background: url('backgrounds/Group-1170.png') center center/cover"
  >
    <RecentModels tags={data.tags} />
    <PopularModels tags={data.tags} />
    <ModelsLeaderboard />
  </div>
  <Posts posts={data.posts} />
  <Consortium />
</div>

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
  import { parseISO, format } from "date-fns";

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
      <div class="w-full md:w-[300px] p-3">
        <div class="h-full flex flex-col gap-3">
          <Events />
          <div>
            <h2
              class="font-bold text-3xl w-full text-left pb-6 text-[rgb(74,191,167)] uppercase"
            >
              Recent posts and news
            </h2>
            {#if data.posts.length > 0}
              {#each data.posts as post}
                <a class="tex-xs flex flex-col gap-2" href="/blog/{post.slug}">
                  <p class="text-gray-400">
                    {format(parseISO(post.date), "MMMM d, yyyy")}
                  </p>
                  <p class="font-bold">{post.title}</p>
                  <p class="text-gray-400">{post.description}</p>
                  <hr class="my-2 border-t border-[rgb(74,191,167)]" />
                </a>
              {/each}
            {/if}
          </div>
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

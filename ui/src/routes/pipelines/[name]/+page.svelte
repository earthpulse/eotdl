<script>
  import auth from "$stores/auth.svelte";
  import { browser } from "$app/environment";
  import { pipelines } from "$stores/pipelines";
  import "$styles/dataset.css";
  import retrievePipeline from "$lib/pipelines/retrievePipeline";
  import deletePipeline from "$lib/pipelines/deletePipeline";
  import Info from "$components/Info.svelte";
  import Metadata from "$components/Metadata.svelte";
  import { fade } from "svelte/transition";
  import EditableTitle from "$components/EditableTitle.svelte";
  import { page } from "$app/stores";
  import retrieveChange from "$lib/changes/retrieveChange";
  import acceptChange from "$lib/changes/acceptChange";
  import declineChange from "$lib/changes/declineChange";
  import { goto } from "$app/navigation";
  import EditableContent from "$components/EditableContent.svelte";
  import FileExplorer from "$components/FileExplorer.svelte";

  $effect(() => {
    load();
  });

  let { data } = $props();

  let pipeline = $state(null);
  let pipeline0 = $state(null);
  let version = $state(null);
  let message = $state(null);
  let curent_image = $state(null);
  let _change = $state(null);
  let change = $state(false);

  const load = async () => {
    if ($page.url.searchParams.get("change")) {
      try {
        _change = await retrieveChange(
          $page.url.searchParams.get("change"),
          auth.id_token,
        );
        pipeline = _change.payload;
        change = true;
      } catch (error) {
        alert("Error retrieving change");
      }
    } else {
      pipeline = await retrievePipeline(data.name);
      pipeline0 = { ...pipeline, metadata: { ...pipeline.metadata } };
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    console.log("copied to clipboard");
    message = "Copied!";
    setTimeout(() => {
      message = null;
    }, 1000);
  };

  let edit = $state(false);

  const save = () => {
    edit = !edit;
    pipelines.update(pipeline, auth.id_token);
    if (pipeline.uid != auth.user.uid) {
      pipeline = { ...pipeline0, metadata: { ...pipeline0.metadata } };
      alert("Your changes have been notified to the pipeline owner.");
    }
  };

  const close = () => {
    pipeline = { ...pipeline0, metadata: { ...pipeline0.metadata } };
    edit = false;
  };

  const accept = async () => {
    try {
      await acceptChange($page.url.searchParams.get("change"), auth.id_token);
      change = false;
      await goto(`/pipelines/${pipeline.name}`);
      load();
    } catch (error) {
      console.log(error);
      alert("Error accepting change");
    }
  };

  const decline = async () => {
    try {
      await declineChange($page.url.searchParams.get("change"), auth.id_token);
      change = false;
      await goto(`/pipelines/${$page.params.name}`);
      load();
    } catch (error) {
      console.log(error);
      alert("Error declining change");
    }
  };

  const deactivatepipeline = async () => {
    if (confirm("Are you sure you want to deactivate this pipeline?")) {
      deletepipeline(pipeline.id, auth.id_token);
      await goto(`/pipelines`);
    }
  };
</script>

<svelte:head>
  <title>EOTDL | {data.name}</title>
</svelte:head>

{#if pipeline}
  <div class="w-full flex flex-col items-center">
    <div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-2">
      <div class="flex flex-col sm:flex-row justify-between w-full gap-3">
        <span class="flex flex-col sm:flex-row gap-2">
          <span class="flex sm:justify-start justify-center">
            <img
              class="w-36 h-36 bg-white object-cover"
              src={pipeline.metadata.thumbnail
                ? pipeline.metadata.thumbnail
                : `${curent_image}`}
              alt=""
            />
          </span>
          <span>
            <!-- <h1 class="text-3xl">{pipeline.name}</h1> -->
            <EditableTitle bind:text={pipeline.name} {edit} />
            <div class="flex flex-wrap gap-1">
              {#each pipeline.tags as tag}
                <p
                  class="badge border-0 text-slate-200 text-xs"
                  style="background-color: {data.tags?.find(
                    (t) => t.name == tag,
                  ).color || 'none'};"
                >
                  {tag}
                </p>
              {/each}
            </div>
            <Info
              data={pipeline}
              store={pipelines}
              field="liked_pipelines"
              bind:version
            />
          </span>
        </span>
        <span class="flex flex-row gap-2">
          {#if !change}
            <span class="flex flex-row gap-2">
              {#if auth.user}
                {#if edit}
                  <button class="btn btn-outline" onclick={save}>Save</button>
                  <button class="btn btn-outline" onclick={close}>Close</button>
                {:else}
                  <button class="btn btn-outline" onclick={() => (edit = !edit)}
                    >Edit</button
                  >
                {/if}
              {/if}
            </span>
          {:else if pipeline.uid == auth.user.uid && _change.status == "pending"}
            <span>
              <button class="btn btn-outline" onclick={accept}>Accept</button>
              <button class="btn btn-outline" onclick={decline}>Decline</button>
            </span>
          {/if}
          {#if auth.user?.uid == pipeline.uid}
            <span>
              <button class="btn btn-outline" onclick={deactivatepipeline}
                >Delete</button
              >
            </span>
          {/if}
        </span>
      </div>
      <hr class="sm:hidden" />
      <div
        class="sm:grid sm:grid-cols-[auto_350px] sm:gap-3 flex flex-col mt-5"
      >
        <div class="w-full overflow-auto">
          <EditableContent {edit} bind:value={pipeline.metadata.description} />
        </div>
        <div class="flex flex-col gap-3 text-xs sm:mt-0 mt-16">
          <hr class="sm:hidden" />
          <p>Stage the pipeline with the CLI:</p>
          <div class="relative">
            <pre class="bg-gray-200 p-3 overflow-x-auto"><button
                onclick={() =>
                  copyToClipboard(
                    `eotdl pipelines get ${pipeline.name} -v ${version?.version_id}`,
                  )}
                >eotdl pipelines get {pipeline.name} -v {version?.version_id}</button
              ></pre>
            {#if message}
              <span
                class="text-gray-400 absolute bottom-[-20px] right-0"
                in:fade
                out:fade>{message}</span
              >
            {/if}
          </div>
          <div class="flex flex-col gap-3">
            <Metadata
              bind:authors={pipeline.metadata.authors}
              bind:license={pipeline.metadata.license}
              bind:source={pipeline.metadata.source}
              {edit}
            />
            <FileExplorer {version} collection={pipeline.name} />
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<script>
  import auth from "$stores/auth.svelte";
  import { browser } from "$app/environment";
  import { datasets } from "$stores/datasets";
  import "$styles/dataset.css";
  import deleteDataset from "$lib/datasets/deleteDataset";
  import retrieveDataset from "$lib/datasets/retrieveDataset";
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

  let { data } = $props();

  $effect(() => {
    load();
    loadDatasets();
  });

  let dataset = $state(null);
  let dataset0 = $state(null);
  let version = $state(null);
  let message = $state(null);
  let description = $state(null);
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
        dataset = _change.payload;
        change = true;
      } catch (error) {
        alert("Error retrieving change");
      }
    } else {
      dataset = await retrieveDataset(data.name);
      dataset0 = { ...dataset, metadata: { ...dataset.metadata } };
    }
  };

  const loadDatasets = async () => {
    await datasets.retrieve(fetch);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    console.log("copied to clipboard");
    message = "Copied!";
    setTimeout(() => {
      message = null;
    }, 1000);
  };

  let upgradeNotebook = $state("");

  $effect(() => {
    if (dataset?.quality == 0) upgradeNotebook = "03_q1_datasets";
    else if (dataset?.quality == 1) upgradeNotebook = "04_q2_datasets";
    else upgradeNotebook = "";
  });

  let edit = $state(false);

  const save = () => {
    edit = !edit;
    datasets.update(dataset, auth.id_token);
    if (dataset.uid != auth.user.uid) {
      dataset = { ...dataset0, metadata: { ...dataset0.metadata } };
      alert("Your changes have been notified to the dataset owner.");
    }
  };

  const close = () => {
    dataset = { ...dataset0, metadata: { ...dataset0.metadata } };
    edit = false;
  };

  const accept = async () => {
    try {
      await acceptChange($page.url.searchParams.get("change"), auth.id_token);
      change = false;
      await goto(`/datasets/${dataset.name}`);
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
      await goto(`/datasets/${$page.params.name}`);
      load();
    } catch (error) {
      console.log(error);
      alert("Error declining change");
    }
  };

  const deactivateDataset = async () => {
    if (confirm("Are you sure you want to deactivate this dataset?")) {
      deleteDataset(dataset.id, auth.id_token);
      await goto(`/datasets`);
    }
  };
</script>

<svelte:head>
  <title>EOTDL | {data.name}</title>
</svelte:head>

{#if dataset}
  <div class="w-full flex flex-col items-center">
    <div class="px-3 py-10 mt-10 w-full max-w-6xl flex flex-col gap-2">
      <div class="flex flex-col sm:flex-row justify-between w-full gap-3">
        <span class="flex flex-col sm:flex-row gap-2">
          <span class="flex sm:justify-start justify-center">
            <img
              class="w-36 h-36 bg-white object-cover"
              src={dataset.metadata.thumbnail
                ? dataset.metadata.thumbnail
                : `${curent_image}`}
              alt=""
            />
          </span>
          <span>
            <!-- <h1 class="text-3xl">{dataset.name}</h1> -->
            <EditableTitle bind:text={dataset.name} {edit} />
            <div class="flex flex-wrap gap-1">
              {#each dataset.tags as tag}
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
              data={dataset}
              store={datasets}
              field="liked_datasets"
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
          {:else if dataset.uid == auth.user.uid && _change.status == "pending"}
            <span>
              <button class="btn btn-outline" onclick={accept}>Accept</button>
              <button class="btn btn-outline" onclick={decline}>Decline</button>
            </span>
          {/if}
          {#if auth.user?.uid == dataset.uid}
            <span>
              <button class="btn btn-outline" onclick={deactivateDataset}
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
          <EditableContent {edit} bind:value={dataset.metadata.description} />
        </div>
        <div class="flex flex-col gap-3 text-xs sm:mt-0 mt-16">
          <hr class="sm:hidden" />
          <p>Stage the dataset with the CLI:</p>
          <div class="relative">
            <pre class="bg-gray-200 p-3 overflow-x-auto"><button
                onclick={() =>
                  copyToClipboard(
                    `eotdl datasets get ${dataset.name} -v ${version?.version_id}`,
                  )}
                >eotdl datasets get {dataset.name} -v {version?.version_id}</button
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
              bind:authors={dataset.metadata.authors}
              bind:license={dataset.metadata.license}
              bind:source={dataset.metadata.source}
              {edit}
            />
            <FileExplorer {version} collection={dataset.name} />
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<script>
  import "../styles/app.css";
  import Nav from "./Nav.svelte";
  import Nav2 from "./Nav2.svelte";
  import Footer from "./Footer.svelte";
  import auth from "$stores/auth.svelte";
  import notifications from "$stores/notifications.svelte";
  import Banner from "./Banner.svelte";

  let { data, children } = $props();
  let loading = $derived(!data?.user);

  $effect(() => {
    if (data?.user) auth.user = data.user;
    if (data?.id_token) auth.id_token = data.id_token;
  });

  const me = async () => {
    const res = await fetch("/api/auth/me");
    if (res.status != 200) {
      loading = false;
      return;
    }
    const data = await res.json();
    auth.user = data.user;
    auth.id_token = data.id_token;
    notifications.retrieve(data.id_token);
    loading = false;
  };

  // retrieve user info client-side from API
  $effect(() => {
    me();
  });
</script>

<svelte:head>
  <title>EOTDL</title>
  <meta
    name="description"
    content="EOTDL is a platform for sharing and discovering training Datasets and Models for Earth Observation applications."
  />
  <meta
    name="keywords"
    content="Earth Observation, Training Datasets, Machine Learning Models, Remote Sensing, Satellite Imagery, AI for Earth Observation"
  />
  <meta name="author" content="Earthpulse" />
  <meta
    property="og:title"
    content="EOTDL - Earth Observation Training Data Lab"
  />
  <meta
    property="og:description"
    content="EOTDL is a platform for sharing and discovering training Datasets and Models for Earth Observation applications."
  />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://eotdl.com" />
  <meta
    property="og:image"
    content="https://eotdl.com//logos/philab-esa_logo.jpg"
  />
  <meta name="twitter:card" content="summary_large_image" />
  <meta
    name="twitter:title"
    content="EOTDL - Earth Observation Training Data Lab"
  />
  <meta
    name="twitter:description"
    content="EOTDL is a platform for sharing and discovering training Datasets and Models for Earth Observation applications."
  />
  <meta
    name="twitter:image"
    content="https://eotdl.com/logos/philab-esa_logo.jpg"
  />
</svelte:head>

<main class="min-h-screen flex flex-col items-center justify-between">
  <div class="w-full h-full grow flex flex-col">
    <!-- <Banner /> -->
    <Nav />
    <div class="relative grow flex flex-col">
      {@render children()}
      <div class="absolute top-0 left-0 w-full">
        <Nav2 {loading} />
      </div>
    </div>
  </div>
  <Footer />
</main>

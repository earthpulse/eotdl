<script>
    let { dataset } = $props();
</script>

<a
    href={`https://radiantearth.github.io/stac-browser/#/external/api.eotdl.com/stac/collections/${dataset.name}`}
    class="btn btn-outline"
    target="_blank">Open in STAC Browser</a
>

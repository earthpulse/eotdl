<script>
	import { onDestroy, onMount, setContext } from "svelte";
	import { browser } from "$app/environment";
	import TileLayer from "./TileLayer.svelte";
	import "$styles/map.css";

	export let geojson;
	export let geotif;

	// $: console.log(geojson);

	let map = null;
	let zoomPosition = "bottomright";
	let options = {
		attributionControl: false,
		max_zoom: 20,
	};

	onMount(async () => {
		if (browser && !map) {
			const L = await import("leaflet");
			await import("georaster-layer-for-leaflet");
			await import("georaster");
			map = L.map("map", options);
			map.zoomControl.setPosition(zoomPosition);
			if (geotif) {
				parseGeoraster(geotif).then((georaster) => {
					const layer = new GeoRasterLayer({
						georaster: georaster,
						opacity: 0.5,
						resolution: 32,
					}).addTo(map);
					const bounds = layer.getBounds();
					map.fitBounds(bounds);
				});
			}
			if (geojson) {
				const layer = L.geoJSON(geojson, {
					// zoom map on click
					onEachFeature: (feature, layer) => {
						layer.on("click", () => {
							map.fitBounds(layer.getBounds());
							// show properties on click
							const properties = feature.properties;
							// const popupContent = Object.keys(properties)
							const popupContent = ["id"]
								.map((key) => {
									return `<strong>${key}</strong>: ${properties[key]}`;
								})
								.join("<br>");
							layer.bindPopup(popupContent).openPopup();
						});
					},
				}).addTo(map);
				const bounds = layer.getBounds();
				map.fitBounds(bounds);
			}
		}
	});

	onDestroy(() => {
		map = null;
	});

	setContext("map", {
		getMap: () => map,
	});
</script>

<div id="map">
	{#if map}
		<TileLayer
			url={"https://api.maptiler.com/maps/dataviz/{z}/{x}/{y}.png?key=PYY1QwzBVjclbEvZmYrO"}
			options={{ maxZoom: 20, zIndex: 1 }}
		/>
	{/if}
</div>

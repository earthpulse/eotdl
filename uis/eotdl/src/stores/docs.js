import { readable } from 'svelte/store';

export const docs = readable({
	api_url: 'https://api.eotdl.com',
});

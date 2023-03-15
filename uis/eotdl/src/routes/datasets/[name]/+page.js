import { EOTDL_API } from '$lib/env';
import retrieveTags from '$lib/tags/retrieveTags';

export const load = async ({params, fetch}) => {
	const url = `${EOTDL_API}/datasets?name=${params.name}`;
	const res = await fetch(url)
	const dataset = await res.json();
	const tags = await retrieveTags(fetch)
	if (res.status == 200) 
		return { dataset, tags };
	return { error: data.detail };
}
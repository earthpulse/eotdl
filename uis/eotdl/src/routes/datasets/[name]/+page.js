import { EOTDL_API } from '$lib/env';

export const load = async ({params, fetch}) => {
	const url = `${EOTDL_API}/datasets?name=${params.name}`;
	const res = await fetch(url)
	const dataset = await res.json();
	if (res.status == 200) 
		return { dataset };
	return { error: data.detail };
}
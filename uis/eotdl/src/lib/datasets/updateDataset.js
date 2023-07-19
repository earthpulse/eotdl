import { PUBLIC_EOTDL_API } from '$env/static/public';
import fetchEOTDL from '$lib/shared/fetchEOTDL';

export default async (dataset_id, name, content, authors, source, license, tags, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets/${dataset_id}`;
	const body = {}
	if(name) body.name = name
	if (content) body.description = content
	if (authors) body.authors = authors
	if (source) body.source = source
	if (license) body.license = license
	body.tags = tags
	const { data, error } = await fetchEOTDL(url, token, 'PUT', body);
	if (error) throw new Error(error);
	return data;
};

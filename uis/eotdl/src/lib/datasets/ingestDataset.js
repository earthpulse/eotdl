import { EOTDL_API } from '$lib/env';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';

export default async (file, name, token) => {
	const url = `${EOTDL_API}/datasets/ingest`;
	const formData = new FormData();
	formData.append("file", file);
	formData.append("name", name);
	const { data, error } = await EOTDLFileUpload(url, token, formData);
	if (error) throw new Error(error);
	return data;
};

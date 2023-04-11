import { EOTDL_API } from '$lib/env';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';

export default async (file, name, description, token) => {
	const url = `${EOTDL_API}/datasets`;
	const formData = new FormData();
	formData.append("file", file);
	formData.append("name", name);
	formData.append("description", description);
	const { data, error } = await EOTDLFileUpload(url, token, formData);
	if (error) throw new Error(error);
	return data;
};

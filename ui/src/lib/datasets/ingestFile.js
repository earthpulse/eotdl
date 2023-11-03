import { PUBLIC_EOTDL_API } from '$env/static/public';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';

export default async (dataset_id, file, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets/${dataset_id}`;
	const formData = new FormData();
	formData.append("file", file);
	const { data, error } = await EOTDLFileUpload(url, token, formData);
	if (error) throw new Error(error);
	return data;
};

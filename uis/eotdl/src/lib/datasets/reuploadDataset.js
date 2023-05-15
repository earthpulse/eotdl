import { PUBLIC_EOTDL_API } from '$env/static/public';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';

export default async (file, dataset_id, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets`;
	const formData = new FormData();
	formData.append("file", file);
	formData.append("dataset_id", dataset_id);
	const { data, error } = await EOTDLFileUpload(url, token, formData, 'PUT');
	if (error) throw new Error(error);
	return data;
};

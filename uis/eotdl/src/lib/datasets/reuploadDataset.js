import { PUBLIC_EOTDL_API } from '$env/static/public';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';

export default async (dataset_id, file, name, content, author, link, license, tags, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets`;
	const formData = new FormData();
	formData.append("dataset_id", dataset_id);
	if (file) formData.append("file", file);
	if(name) formData.append("name", name);
	if (content) formData.append("content", content);
	if (author) formData.append("author", author);
	if (link) formData.append("link", link);
	if (license) formData.append("license", license);
	formData.append("tags", tags);
	const { data, error } = await EOTDLFileUpload(url, token, formData, 'PUT');
	if (error) throw new Error(error);
	return data;
};

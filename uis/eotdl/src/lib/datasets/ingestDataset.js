import { PUBLIC_EOTDL_API } from '$env/static/public';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';

export default async (file, name, author, link, license, description, tags, token) => {
	const url = `${PUBLIC_EOTDL_API}/datasets`;
	const formData = new FormData();
	formData.append("file", file);
	formData.append("name", name);
	formData.append("author", author);
	formData.append("link", link);
	formData.append("license", license);
	formData.append("tags", tags);
	formData.append("description", description);
	const { data, error } = await EOTDLFileUpload(url, token, formData);
	if (error) throw new Error(error);
	return data;
};

import { PUBLIC_EOTDL_API } from '$env/static/public';
import EOTDLFileUpload from '$lib/shared/EOTDLFileUpload';
// import fileChecksum from '../datasets/fileChecksum';

export default async (model_id, file, token, version) => {
	const url = `${PUBLIC_EOTDL_API}/models/${model_id}?version=${version.version}`;
	const formData = new FormData();
	formData.append("file", file);
	// formData.append("checksum", fileChecksum(await file.arrayBuffer()));
	const { data, error } = await EOTDLFileUpload(url, token, formData);
	if (error) throw new Error(error);
	return data;
};

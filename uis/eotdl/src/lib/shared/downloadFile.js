import { createWriteStream } from 'streamsaver';

export const downloadFile = (url, token, fileName) => {
  return fetch(url, {
		method: "GET",
		headers: {
			Authorization: `Bearer ${token}`,
		},
	}).then(res => {
		const fileStream = createWriteStream(fileName);
		const writer = fileStream.getWriter();
		if (res.body.pipeTo) {
		writer.releaseLock();
		return res.body.pipeTo(fileStream);
		}

		const reader = res.body.getReader();
		const pump = () =>
		reader
			.read()
			.then(({ value, done }) => (done ? writer.close() : writer.write(value).then(pump)));

		return pump();
	});
};
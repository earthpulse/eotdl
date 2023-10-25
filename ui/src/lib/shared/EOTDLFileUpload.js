export default async (url, token, body, method) => {
  const res = await fetch(url, {
    method: method || 'POST',
    headers: {
      // 'Content-Type': 'multipart/form-data',
      Authorization: `Bearer ${token}`
    },
    body
  });
  const data = await res.json();
  if (res.status == 200) {
    return { data };
  }
  return { error: data.detail };
};

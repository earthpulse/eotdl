export default async (url, method, headers, body) => {
  const res = await fetch(url, {
    method: method || 'GET',
    headers,
    body: body && JSON.stringify(body)
  });
  const data = await res.json();
  if (res.status == 200) {
    return { data };
  }
  return { error: data.detail };
};

export default async (url, token, method, body) => {
  const res = await fetch(url, {
    method: method || "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: body && JSON.stringify(body),
  });
  const data = await res.json();
  if (res.status == 200) {
    return { data };
  }
  return { error: data.detail };
};

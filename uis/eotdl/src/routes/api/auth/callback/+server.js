import { retrieveToken } from "$lib/auth/auth0";

export async function GET(event) {
  // get code from auth0 response
  const code = event.url.searchParams.get("code");
  const redirect_uri = `http://${event.request.headers.get("host")}/`;
  // retrieve toksn
  const { error, id_token } = await retrieveToken(code, redirect_uri);
  if (error) 
    return Response.error(500, error);
  // redirect with token in cookie
  return new Response(null, {
    status: 302,
    headers: {
      "Location": redirect_uri,
      "Set-Cookie": `id_token=${id_token}; Path=/; HttpOnly; SameSite=Lax`,
    },
  });
}

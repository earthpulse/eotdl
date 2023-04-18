import { AUTH0_CLIENT_ID, AUTH0_DOMAIN } from '$env/static/private';

export async function GET(event) {
  const returnTo = `http://${event.url.host}`; 
  return new Response(null,{
    status: 302,
    headers: {
      location: `https://${AUTH0_DOMAIN}/v2/logout?returnTo=${returnTo}&cliend_id=${AUTH0_CLIENT_ID}`,
      "Set-Cookie": `id_token=; Path=/; HttpOnly; SameSite=Lax; expires=Thu, 01 Jan 1970 00:00:00 GMT`,
    },
  })
}

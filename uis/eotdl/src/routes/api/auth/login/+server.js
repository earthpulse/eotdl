import { AUTH0_DOMAIN, AUTH0_CLIENT_ID } from "$lib/env";

export async function GET({url}) {
  const redirect_uri = `http://${url.host}/api/auth/callback`; 
  const login_url = `https://${AUTH0_DOMAIN}/authorize?response_type=code&scope=openid profile email&client_id=${AUTH0_CLIENT_ID}&redirect_uri=${redirect_uri}`;
  return Response.redirect(login_url, 302)
}

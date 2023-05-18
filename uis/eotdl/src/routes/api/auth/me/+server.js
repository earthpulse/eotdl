import { verifyToken } from "$lib/auth/auth0";
import cookie from "cookie";
import fetch from 'isomorphic-unfetch'
import retrieveUserData from '../../../../lib/auth/retrieveUserData';


export async function GET(event) {
  const cookies = cookie.parse(event.request.headers.get("cookie") || "");
  if (cookies?.id_token) {
    try {
      const user = await verifyToken(cookies.id_token);
      const userData = await retrieveUserData(cookies.id_token, fetch)
      if (!user)  return new Response('unauthorized', {status: 401})
      return new Response(JSON.stringify({user: userData, id_token: cookies.id_token}))
    } catch (error) {
      return new Response('unauthorized', {status: 401})
    }
  }
  return new Response('unauthorized', {status: 401})
}
  
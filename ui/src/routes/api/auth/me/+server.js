import retrieveUserData from '$lib/auth/retrieveUserData';

export async function GET({ locals }) {
  if (!locals?.user || !locals?.id_token) {
    return new Response("unauthorized", { status: 401 });
  }
  const userData = await retrieveUserData(locals.id_token, fetch)
  return new Response(
    JSON.stringify({ user: userData, id_token: locals.id_token }),
  );
}


export async function GET({ locals }) {
  if (!locals?.user || !locals?.id_token) {
    return new Response("unauthorized", { status: 401 });
  }
  return new Response(
    JSON.stringify({ user: locals.user, id_token: locals.id_token }),
  );
}
  

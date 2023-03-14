export async function GET({ locals }) {
    const user = { locals };
    if (!user) 
      return Response.error(401, "unauthorized");
    return new Response(JSON.stringify(user))
}
  
export const GET = async ({ locals, url }) => {
  await locals.logtoClient.signOut(url.origin);
};

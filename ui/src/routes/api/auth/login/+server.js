import { redirect } from '@sveltejs/kit';

export const GET = async ({ locals, url }) => {
  await locals.logtoClient.signIn(`${url.origin}/callback`);
};

import { redirect } from '@sveltejs/kit';
import retrieveUserData from '$lib/auth/retrieveUserData';
import retrieveUserCredentials from '$lib/auth/retrieveUserCredentials';

export async function load({ locals, fetch }) {
    if (!locals?.user) 
        throw redirect(307, '/api/auth/login');
    const userData = await retrieveUserData(locals.id_token, fetch)
    const credentials = await retrieveUserCredentials(locals.id_token, fetch)
    userData.credentials = credentials
    return {
        id_token: locals.id_token,
        user: userData
    }
}

export const prerender = false;
import { redirect } from '@sveltejs/kit';
import retrieveUserData from '../../lib/auth/retrieveUserData';

export async function load({ locals, fetch }) {
    if (!locals?.user) 
        throw redirect(307, '/api/auth/login');
    const userData = await retrieveUserData(locals.id_token, fetch)
    return {
        id_token: locals.id_token,
        user: userData
    }
}

export const prerender = false;
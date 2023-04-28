import { redirect } from '@sveltejs/kit';

export async function load({ locals }) {
    if (!locals?.user) 
        throw redirect(307, '/api/auth/login');
    return locals
}

export const prerender = false;
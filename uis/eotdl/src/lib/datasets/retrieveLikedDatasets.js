import { EOTDL_API } from '$lib/env';

export default async (fetch, token) => {
    let url = `${EOTDL_API}/datasets/liked`;
    try {
        const res = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            });
            const data = await res.json();
            if (res.status == 200) 
            return data
            throw new Error(data.detail);
    } catch (err) {
        return []
    }
};

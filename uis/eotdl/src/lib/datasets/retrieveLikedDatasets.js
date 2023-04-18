import { PUBLIC_EOTDL_API } from '$env/static/public';

export default async (fetch, token) => {
    let url = `${PUBLIC_EOTDL_API}/datasets/liked`;
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

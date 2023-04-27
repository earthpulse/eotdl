export async function load({parent}) {
    console.log("ei")
    const data = await parent()
    console.log(data)
    return {}
}


export const prerender = true;
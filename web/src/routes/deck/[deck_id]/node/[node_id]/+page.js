export async function load({ params, url, fetch }) {
    const { deck_id, node_id } = params;
    const response = await fetch(`/api/node/load/${node_id}/`);
    const node = await response.json();
    return { node };
}

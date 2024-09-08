export async function load({ params, url, fetch }) {
    const response = await fetch(`/api/db/query/deck/?order_by=update_time__desc`);
    const decks = await response.json(); 
    return { decks };
}

export async function load({ params, url, fetch }) {
    console.log("deck")
    const {deck_id} = params;
    const response = await fetch(`/api/deck/load/${deck_id}/`);
    const data = await response.json(); 
    data['deck_id'] = deck_id;
    return data;
}

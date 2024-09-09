<script>
  import axios from 'axios';
  import { Button, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';

  export let data;
    
  function handleNewDeck() {
    // Placeholder for new deck creation logic
    console.log(data.decks);
    console.log('New deck button clicked');
    
    let deckName = prompt('Enter the name for the new deck:');
    if (deckName) {
      console.log('New deck name:', deckName);
    } else {
      console.log('Deck creation cancelled');
      return;
    }
    axios.post('/api/deck/create/', { name: deckName })
      .then(response => {
        console.log('Deck created:', response.data);
        // Refresh the page to show the newly created deck
        window.location.reload();
      })
      .catch(error => {
        console.error('Error creating deck:', error);
        alert('Error creating deck');
      });
  }
</script>

<div class="container mx-auto p-4">
  <Button class="mb-4" on:click={handleNewDeck}>New</Button>

  <Table>
    <TableHead>
      <TableHeadCell>ID</TableHeadCell>
      <TableHeadCell>Name</TableHeadCell>
      <TableHeadCell>Update Time</TableHeadCell>
      <TableHeadCell>Actions</TableHeadCell>
    </TableHead>
    <TableBody>
      {#each data.decks as deck}
        <TableBodyRow>
          <TableBodyCell>{deck.id}</TableBodyCell>
          <TableBodyCell>{deck.name}</TableBodyCell>
          <TableBodyCell>{deck.update_time}</TableBodyCell>
          <TableBodyCell>
            <Button href="/web/deck/{deck.id}/">Edit Slides</Button>
            <Button disabled>Present</Button>
          </TableBodyCell>
        </TableBodyRow>
      {/each}
    </TableBody>
  </Table>
</div>

<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { linearize } from '$lib/deck_tree';
	export let data;

	onMount(async () => {
		console.log(data);
		let linearized = linearize(data.root);
		console.log(linearized);
        for (let node of linearized) {
			if (node.children === undefined) {
				goto(`/web/deck/${data.deck_id}/node/${node.node_id}/`);
				return;
			}
		}
		alert("No slides found");
	});
</script>

<div>Redirecting...</div>

<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import Sortable from 'sortablejs';
    export let deck_id;
    export let slides;
    let showMenuLinearIndex = null;    // if not null this is the linearIndex of the selected slide

    onMount(() => {
        new Sortable(document.getElementById('items'), {
            animation: 150,
            easing: "cubic-bezier(1,0,0,1)",
            onEnd: (event) => {
                let oldIndex = event.oldIndex;
                let newIndex = event.newIndex;
                dispatch('reorderSlide', { oldIndex, newIndex });
            }
        });

        const handleClickOutside = (event) => {
            showMenuLinearIndex = null;
        };

        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    });

    const dispatch = createEventDispatcher();

    const handleInsertSlide = (linearIndex, after) => {
        dispatch('insertSlide', { linearIndex, after });
        showMenuLinearIndex = null;
    };

    const handleDeleteSlide = (linearIndex) => {
        dispatch('deleteSlide', { linearIndex });
        showMenuLinearIndex = null;    
    };

</script>    

<div>
<ul id="items">
    {#each slides as slide}    
	<li>
        <div class="relative group">            
            <div class="flex p-2 items-center w-full cursor-pointer hover:opacity-75 transition-opacity"
                 on:contextmenu|preventDefault={() => showMenuLinearIndex = slide.linearIndex}>
                {#if slide.isNode}
                    {#if slide.isSlide}
                        {#if showMenuLinearIndex === slide.linearIndex}
                        <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                            <div class="py-1">
                                <button class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" on:click={() => handleInsertSlide(slide.linearIndex, false)}>
                                    Insert above    
                                </button>
                                <button class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" on:click={() => handleInsertSlide(slide.linearIndex, true)}>
                                    Insert below
                                </button>
                                <button class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100" on:click={() => handleDeleteSlide(slide.linearIndex)}>
                                    Delete
                                </button>
                            </div>
                            </div>
                        {/if}                        
                        <span class="mr-2 text-lg font-semibold">{slide.slideIndex}</span>
                        <a href="/web/deck/{deck_id}/node/{slide.node_id}/" class="flex-grow">
                            <img src="data:image/png;base64,{slide.thumb}" class="w-full h-auto object-cover rounded shadow-md" style="width: 100%; height: auto;" />
                        </a>
                    {:else}
                        <a href="/web/deck/{deck_id}/node/{slide.node_id}/" class="flex-grow">
                        <span class="mr-2 text-lg font-semibold">{slide.label}</span>
                        </a>
                    {/if}
                {:else}
                    <span class="mr-2 text-lg font-semibold">---</span>
                {/if}
            </div>
        </div>
    </li>
    {/each}
</ul>
</div>
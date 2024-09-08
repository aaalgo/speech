<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import Sortable from 'sortablejs';
    export let deck_id;
    export let slides;
    let showMenu = null;

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
            showMenu = null;
        };

        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    });

    const dispatch = createEventDispatcher();

    const handleInsertSlide = (slideIndex) => {
        dispatch('insertSlide', { slideIndex });
        showMenu = null;
    };

    const handleDeleteSlide = (slideIndex) => {
        dispatch('deleteSlide', { slideIndex });
        showMenu = null;    
    };

</script>    

<div>
<ul id="items">
    {#each slides as slide}    
	<li>
        <div class="relative group">            
            {#if showMenu === slide.id}
                <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                    <div class="py-1">
                        <button class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" on:click={() => handleInsertSlide(slides.indexOf(slide))}>
                            Insert above
                        </button>
                        <button class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" on:click={() => handleInsertSlide(slides.indexOf(slide)+1)}>
                            Insert below
                        </button>
                        <button class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100" on:click={() => handleDeleteSlide(slides.indexOf(slide))}>
                            Delete
                        </button>
                    </div>
                </div>
            {/if}
            <div class="flex p-2 items-center w-full cursor-pointer hover:opacity-75 transition-opacity"
                 on:contextmenu|preventDefault={() => showMenu = slide.id}>
                <span class="mr-2 text-lg font-semibold">{slide.index+1}</span>
                <a href="/web/deck/{deck_id}/slide/{slide.id}/" class="flex-grow">
                    <img src="data:image/png;base64,{slide.thumb}" alt={`Slide ${slide.id}`} class="w-full h-auto object-cover rounded shadow-md" style="width: 100%; height: auto;" />
                </a>
            </div>
        </div>
    </li>
    {/each}
</ul>
</div>
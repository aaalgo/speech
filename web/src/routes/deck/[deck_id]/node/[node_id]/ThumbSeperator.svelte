<script>
    let showContextMenu = false;
    export let offset;

    const handleThumbSeperatorContextMenu = (event) => {
        event.preventDefault();
        showContextMenu = true;
    };
    
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();

    const handleAddSlide = () => {
        dispatch('addSlide', { offset });
        showContextMenu = false;
    };

    // Close context menu when clicking outside
    const handleClickOutside = (event) => {
        if (showContextMenu && !event.target.closest('.context-menu')) {
            showContextMenu = false;
        }
    };

    $: if (showContextMenu) {
        document.addEventListener('click', handleClickOutside);
    } else {
        document.removeEventListener('click', handleClickOutside);
    }

</script>

<div class="col-span-2 relative">
    <hr class="border-t-4 border-gray-300 my-2 cursor-pointer hover:border-blue-500 transition-colors duration-200" on:contextmenu|preventDefault={handleThumbSeperatorContextMenu} />
    {#if showContextMenu}
        <div class="absolute left-0 mt-1 w-40 bg-white rounded-md shadow-lg z-10">
            <ul class="py-1">
                <li>
                    <button class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" on:click={handleAddSlide}>
                        Add slide
                    </button>
                </li>
            </ul>
        </div>
    {/if}
</div>

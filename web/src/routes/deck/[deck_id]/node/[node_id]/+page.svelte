<script>
    import { tick } from 'svelte';
    import { invalidate, goto } from '$app/navigation';
    import { Tabs, TabItem, Input, Textarea, Label, Button, Spinner } from 'flowbite-svelte';
    import DeckIndex from './DeckIndex.svelte';
    import { linearize } from '$lib/deck_tree';
    export let data;

    let leftPanelWidth = 10; // Initial width in percentage
    function handleDrag(e) {
        const containerWidth = e.target.parentElement.offsetWidth;
        const newWidth = (e.clientX / containerWidth) * 100;
        leftPanelWidth = Math.max(10, Math.min(90, newWidth));
    }

    function updateLinearized(current, root) {
        let linearized = linearize(root);
        let slideIndex = 1;
        current.isSlide = false;
        current.slideIndex = undefined;
        for (let i = 0; i < linearized.length; i++) {
            let node = linearized[i];
            node.linearIndex = i;
            node.isSlide = false;
            node.isNode = true;
            if (node.ref !== undefined) {
                node.isNode = false;
            }
            else if (node.children === undefined) {
                // this node is a slide
                node.isSlide = true;
                if (node.thumb === undefined || node.thumb === null) {
                    node.thumb = data.blank_thumb;
                }
                node.slideIndex = slideIndex;
                ++slideIndex;
            }
            if (node.node_id == current.id) {
                current.linearIndex = i;
                current.isSlide = node.isSlide;
                current.slideIndex = node.slideIndex;
            }
        }
        console.log('linearized', linearized);
        return linearized;
    }

    function cleanUpTreeForSave(node) {
        let cleaned = {
            'node_id': node.node_id,
            'label': node.label,
        }
        if (node.children !== undefined) {
            let children = [];
            for (let child of node.children) {
                children.push(cleanUpTreeForSave(child));
            }
            cleaned.children = children;
        }
        return cleaned;    
    }   

    $: linearized = updateLinearized(data.node, data.root);

    function insertNodeIntoTree(node, ref, after) {
        let parent = ref.parent;
        let ref_index = null;
        for (let i = 0; i < parent.children.length; i++) {
            if (parent.children[i].node_id == ref.node_id) {
                ref_index = i;
                break;
            }
        }
        if (ref_index === null) {
            alert('Ref node not found in linearized list');
            return false;
        }
        let left = null;
        let right = null;
        if (after) {
            left = parent.children.slice(0, ref_index + 1);
            right = parent.children.slice(ref_index + 1);
        }
        else {
            left = parent.children.slice(0, ref_index);
            right = parent.children.slice(ref_index);
        }
        parent.children = [...left, node, ...right];
        return true;
    }    

    async function handleInsertSlide(event) {
        // Placeholder for add slide logic
        console.log('Add slide clicked', event.detail.linearIndex);
        let linearIndex = event.detail.linearIndex;        
        let after = event.detail.after;
        let resp = null;
        resp = await fetch('/api/node/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                deck_id: data.deck_id
            })
        });
        if (!resp) {
            alert('Error creating node');   
            return;
        }
        let resp_json = await resp.json();
        let new_node_id = resp_json.id;
        let new_node = {
            'node_id': new_node_id,
            'label': 'New node'
        };
        let ref = linearized[linearIndex];
        if (!insertNodeIntoTree(new_node, ref, after)) {
            alert('Error inserting slide');
            return;
        }
        resp = null;
        resp = await fetch(`/api/deck/save/${data.deck_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                root: cleanUpTreeForSave(data.root)
            })
        });
        if (!resp) {
            alert('Error saving deck');
            return;
        }
        window.location.href = `/web/deck/${data.deck_id}/node/${new_node_id}/`;
    }

    function deleteNodeFromTree(node) {
        let parent = node.parent;
        let index = null;
        for (let i = 0; i < parent.children.length; i++) {
            if (parent.children[i].node_id == node.node_id) {
                index = i;
                break;
            }
        }
        if (index === null) {
            alert('Node not found in linearized list');
            return false;
        }
        parent.children = [...parent.children.slice(0, index), ...parent.children.slice(index + 1)];
        return true;
    }

    async function handleDeleteSlide(event) {
        let linearIndex = event.detail.linearIndex;
        let node = linearized[linearIndex];
        // check node is a slide
        if (!node.isSlide) {
            alert('Node is not a slide');
            return;
        }
        let goto_slide = null;
        if (node.node_id !== data.node.id) {
            goto_slide = data.node.id;
        }
        if (goto_slide === null) {
            for (let i = linearIndex + 1; i < linearized.length; i++) {
                if (linearized[i].isSlide) {
                    goto_slide = linearized[i].node_id;
                    break;
                }
            }
        }
        if (goto_slide === null) {
            for (let i = linearIndex - 1; i >= 0; i--) {
                if (linearized[i].isSlide) {
                    goto_slide = linearized[i].node_id;
                    break;
                }
            }
        }
        if (goto_slide === null) {
            alert('Cannot delete last slide!');
            return;
        }
        if (!deleteNodeFromTree(node)) {
            alert('Error deleting slide');
            return;
        }
        // now we need to post the tree
        let resp = await fetch(`/api/deck/save/${data.deck_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                root: cleanUpTreeForSave(data.root)
            })
        });
        if (!resp) {
            alert('Error saving deck');
            return;
        }
        window.location.href = `/web/deck/${data.deck_id}/node/${goto_slide}/`;
    }   

    async function handleReorderSlide(event) {
        console.log('Reorder slide:', event.detail.oldIndex, event.detail.newIndex);
        let oldLinearIndex = event.detail.oldIndex;
        let newLinearIndex = event.detail.newIndex;
        console.log('oldLinearIndex', oldLinearIndex);
        if (oldLinearIndex == newLinearIndex) {
            return;
        }
        if (newLinearIndex > oldLinearIndex) {
            newLinearIndex += 1;
        }
        let node = linearized[oldLinearIndex];
        let insertRef = linearized[newLinearIndex];
        console.log("insertRef", insertRef.node_id);
        let after = false;
        if (!insertRef.isSlide) {
            // if the ref location is not slide, insert using previous slide
            if (newLinearIndex > 0) {
                insertRef = linearized[newLinearIndex - 1];
                if (!insertRef.isSlide) {
                    alert("Previous node is not a slide, please refresh the page");
                    return;
                }
                after = true;
            }
            else {
                alert("Cannot move slide to top of deck, please refresh the page");
                return;
            }
        }

        if (!deleteNodeFromTree(node)) {
            alert('Error deleting slide');
            return;
        }
        if (!insertNodeIntoTree(node, insertRef, after)) {
            alert('Error inserting slide');
            return;
        }
        let resp = await fetch(`/api/deck/save/${data.deck_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                root: cleanUpTreeForSave(data.root)
            })
        }); 
        if (!resp) {
            alert('Error saving deck');
            return;
        }
        window.location.href = `/web/deck/${data.deck_id}/node/${node.node_id}/`;
    }

    let generationOutput = '';

    async function handleSave() {
        let resp = await fetch(`/api/node/save/${data.node.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: data.node.content,
                hint: data.node.hint
            })
        });
        if (!resp) {
            alert('Error saving node');
            return;
        }
    }

    let loadingSpinner = false;

    async function handleGenerateSlide() {
        loadingSpinner = true;
        let resp = await fetch(`/api/node/generate_slide/${data.node.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: data.node.content,
                hint: data.node.hint
            })
        });
        loadingSpinner = false;
        try {
            let resp_json = await resp.json();
        } catch (error) {
            console.error('Error parsing response:', error);
        }
        linearized[data.node.linearIndex].thumb = resp_json.thumb;
        data.node.image = resp_json.image;
    }

    function handleGenerateScript() {
        handleSave();
        axios.post('/api/deck/generate_script/', {
            slide_id: data.slide.id,
        })
        .then(response => {
            generationOutput = response.data;
        })
        .catch(error => {
            console.error('Error generating script:', error);   
        });
    }

    function handleGenerateAV() {
        axios.post('/api/deck/generate_av/', {
            slide_id: data.slide.id,
        })
        .then(response => { 
            generationOutput = response.data;
        })
        .catch(error => {
            console.error('Error generating AV:', error);
        });
    }       
</script>

<div class="flex h-screen">
    <div class="overflow-y-auto bg-gray-100" style="width: {leftPanelWidth}%;">
    <DeckIndex deck_id={data.deck_id} slides={linearized}
        on:insertSlide={handleInsertSlide} 
        on:deleteSlide={handleDeleteSlide} 
        on:reorderSlide={handleReorderSlide}
    />
    </div>
    <!--
    <div 
        class="w-1 bg-gray-300 cursor-col-resize hover:bg-gray-400 active:bg-gray-500" 
        on:mousedown={() => window.addEventListener('mousemove', handleDrag)}
        on:mouseup={() => window.removeEventListener('mousemove', handleDrag)}
    ></div>
    -->

    <div class="flex-grow overflow-y-auto" style="width: {100 - leftPanelWidth}%;">        
        <div class="p-4">
            {#if data.node.isSlide}
                Slide {data.node.slideIndex} (id: {data.node.id})
            {:else}
                Node {data.node.label} (id: {data.node.id})
            {/if}
        </div>
        
        <div class="flex-grow p-4">
            <Tabs>
                {#if data.node.isSlide}
                <TabItem open title="Outline">
                    <div class="flex">
                        <div class="w-1/2 pr-4">
                            <div class="mb-4">
                                <Label for="slideContent" class="mb-2">Content</Label>
                                <Textarea id="slideContent" rows="4" bind:value={data.node.content} placeholder="Enter your slide content here..." />
                            </div>
                            <div class="mb-4">
                                <Label for="hint" class="mb-2">Hint</Label>
                                <Textarea id="hint" rows="2" bind:value={data.node.hint} placeholder="Enter a hint for generation..." />
                            </div>
                            <Button on:click={handleGenerateSlide}>Generate Slide</Button>
                            <Button on:click={handleGenerateScript}>Generate Script</Button>
                        </div>
                        <div class="w-1/2 pl-4">
                        {#if loadingSpinner}
                            <Spinner />
                        {:else}
                            <div class="mb-4">
                                <Label for="slideImage" class="mb-2">Slide Image</Label>
                                <img id="slideImage" src="data:image/png;base64,{data.node.image}" alt="Slide Image" class="max-h-full w-auto" style="height: 100%; width: auto;" />
                               
                            </div>
                        {/if}
                        </div>
                    </div>

                </TabItem>                
                <TabItem title="Script">                    
                    <div class="mb-4">
                        <Label for="slideScript" class="mb-2">Script</Label>
                        <Textarea id="slideScript" rows="4" bind:value={data.node.script}/>
                    </div>
                    <Button on:click={handleGenerateAV}>Generate Audio/Video</Button>                    

                </TabItem>
                <TabItem title="Audio/Video">
                    <Textarea id="generationOutput" rows="4" bind:value={generationOutput} placeholder="Generated content will appear here..." readonly />
                    <Button on:click={handleGenerateAV}>Generate Audio</Button>
                </TabItem>
                {:else}
                <TabItem open title="Outline">
                    <div class="mb-4">
                        <Label for="hint" class="mb-2">Hint</Label>
                        <Textarea id="hint" rows="4" bind:value={data.node.hint} placeholder="Enter a hint for generation..." />
                    </div>
                    <Button on:click={handleSave}>Save</Button>                    
                </TabItem>                
                {/if}
            </Tabs>
        </div>
    </div>
</div>



<script>
    import { tick } from 'svelte';
    import { invalidate, goto } from '$app/navigation';
    import { Tabs, TabItem, Input, Textarea, Label, Button, Spinner } from 'flowbite-svelte';
    import DeckIndex from './DeckIndex.svelte';
    import { linearize } from '$lib/deck_tree';
    export let data;

    function word_count(text) {
        return text.split(/\s+/).filter(Boolean).length;
    }

    $: script_words = word_count(data.node.script);
    $: menuscript_words = word_count(data.node.menuscript);

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
        if (current.hint === undefined) {
            current.hint = '';
        }
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

    $: linearized = updateLinearized(data.node, data.root);

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

    function cleanupNodeForSave(node) {
        return JSON.stringify({
            content: node.content,
            slideHint: node.slideHint,
            scriptHint: node.scriptHint,
            menuscriptHint: node.menuscriptHint
        });
    }

    async function handleSave() {
        let resp = await fetch(`/api/node/save/${data.node.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: cleanupNodeForSave(data.node)
        });
        if (!resp) {
            alert('Error saving node');
            return;
        }
    }

    let slideSpinner = false;
    let scriptSpinner = false;
    let menuscriptSpinner = false;
    let audioSpinner = false;    
    let videoSpinner = false;
    let activeTab = 'slide'; // Default to 'outline' tab

    async function handleGenerateSlide() {
        slideSpinner = true;
        do {
            let resp = await fetch(`/api/node/generate_slide/${data.node.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: cleanupNodeForSave(data.node)
            });
            if (!resp) {
                alert('Error generating slide');
                break;
            }
            let resp_json = null;
            try {
                resp_json = await resp.json();
                console.log('resp_json', resp_json);
            } catch (error) {
                console.error('Error parsing response:', error);
                break;
            }
            linearized[data.node.linearIndex].thumb = resp_json.thumb;
            data.node.image = resp_json.image;
        } while (false);
        slideSpinner = false;
    }

    async function handleGenerateScript() {
        scriptSpinner = true;
        do {
            let resp = await fetch(`/api/node/generate_script/${data.node.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: cleanupNodeForSave(data.node)
            });
            if (!resp) {
                alert('Error generating script');
                break;
            }
            let resp_json = await resp.json();
            data.node.script = resp_json.script;
            data.node.prompt = resp_json.prompt;
        } while (false);
        scriptSpinner = false;
    }

    async function handleGenerateMenuscript() {
        menuscriptSpinner = true;
        do {
            let resp = await fetch(`/api/node/generate_menuscript/${data.node.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: cleanupNodeForSave(data.node)
            });
            if (!resp) {
                alert('Error generating menuscript');
                break;
            }
            let resp_json = await resp.json();
            data.node.menuscript = resp_json.menuscript;
        } while (false);
        menuscriptSpinner = false;
    }

    async function handleGenerateAudio() {
        audioSpinner = true;
        do {
            let resp = await fetch(`/api/node/generate_audio/${data.node.id}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: cleanupNodeForSave(data.node)
            });
            if (!resp) {
                alert('Error generating AV');
                break;
            }
            let resp_json = await resp.json();            
            data.node.audioUrl = resp_json.audioUrl;
        } while (false);
        audioSpinner = false;
    }       

    async function handleGenerateVideo() {

    }
</script>

<div class="flex h-screen text-lg">
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
        <div class="p-4 text-xl">
            {#if data.node.isSlide}
                Slide {data.node.slideIndex} (id: {data.node.id})
            {:else}
                Node {data.node.label} (id: {data.node.id})
            {/if}
        </div>
        
        <div class="flex-grow p-4 flex">
            <!-- Left side: Content from old "Outline" TabItem -->
            <div class="w-1/2 pr-4">
                <div class="mb-4">
                    <Label for="slideContent" class="mb-2 text-lg">Content</Label>
                    <Textarea id="slideContent" rows="20" bind:value={data.node.content} placeholder="Enter your slide content here..." class="text-xl" />
                </div>
            </div>

            <!-- Right side: Tabs structure -->
            <div class="w-1/2 pl-4">
                {#if data.node.isSlide}
                    <Tabs bind:selected={activeTab}>
                        <TabItem open={activeTab === 'slide'} title="Slide">
                            <div class="mb-4">
                                <Label for="slideHint" class="mb-2 text-lg">Hint</Label>
                                <Textarea id="slideHint" rows="2" bind:value={data.node.slideHint}  placeholder="Enter additional hint for generation..." class="text-lg" />
                            </div>
                            <Button on:click={handleGenerateSlide} class="text-lg" disabled={slideSpinner}>Update</Button>
                            <div class="mb-4 mt-4">
                                {#if slideSpinner}
                                    <Spinner />
                                {:else}
                                    <img id="slideImage" src="data:image/png;base64,{data.node.image}" alt="Slide Image" class="max-h-full w-auto" style="height: 100%; width: auto;" />
                                {/if}
                            </div>
                        </TabItem>
                        <TabItem open={activeTab === 'script'} title="Script">
                            <div class="mb-4">
                                <Label for="scriptHint" class="mb-2 text-lg">Hint</Label>
                                <Textarea id="scriptHint" rows="2" bind:value={data.node.scriptHint}  placeholder="Enter additional hint for generation..." class="text-lg" />
                            </div>
                            <Button on:click={handleGenerateScript} class="text-lg" disabled={scriptSpinner}>Update</Button>
                            {#if scriptSpinner}
                                <Spinner />
                            {:else}
                                <div class="mb-4">
                                    <Tabs>                                        
                                        <TabItem open title="Script">
                                            <Label for="slideScript" class="mb-2 text-lg">Script ({script_words} words)</Label>
                                            <Textarea id="slideScript" rows="16" bind:value={data.node.script} class="text-lg"/>
                                        </TabItem>
                                        <TabItem title="Prompt">
                                            <Label for="slidePrompt" class="mb-2 text-lg">Prompt</Label>
                                            <Textarea id="slidePrompt" rows="16" bind:value={data.node.prompt} class="text-lg"/>
                                        </TabItem>
                                    </Tabs>
                                </div>
                            {/if}
                        </TabItem>
                        <TabItem open={activeTab === 'audio'} title="Audio">
                            <!--
                            <div class="mb-4">
                                <Label for="avHint" class="mb-2 text-lg">Hint</Label>
                                <Textarea id="avHint" rows="2" bind:value={data.node.avHint} placeholder="Enter a hint for generation..." class="text-lg" />
                            </div>
                        -->
                            <Button on:click={handleGenerateAudio} class="text-lg" disabled={audioSpinner}>Update</Button>
                            {#if audioSpinner}
                            <br/>
                                <div class='p-4 mb-4'>
                                    <Spinner /> (Takes about 20s)
                                </div>
                            {:else}
                                {#if data.node.audioUrl}
                                    <div class="mb-4">
                                        <Label for="audioPlayer" class="mb-2 text-lg">Audio</Label>
                                        <audio id="audioPlayer" controls src={data.node.audioUrl}>
                                            Your browser does not support the audio element.
                                        </audio>
                                    </div>
                                    <div class="mb-4">
                                        <Label for="scriptDisplay" class="mb-2 text-lg">Script ({script_words} words)</Label>
                                        <Textarea id="scriptDisplay" rows="32" value={data.node.script} readonly class="text-lg"/>
                                    </div>    
                                {/if}
                            {/if}
                        </TabItem>
                        <TabItem open={activeTab === 'video'} title="Video">
                            <Button on:click={handleGenerateVideo} class="text-lg" disabled={videoSpinner || true}>Generate Video</Button>
                            {#if videoSpinner}
                            <div class='mb-4'>
                                <Spinner />
                            </div>
                            {:else}
                                {#if data.node.videoUrl}
                                    <div class="mb-4">
                                        <Label for="videoPlayer" class="mb-2 text-lg">Video</Label>
                                        <video id="videoPlayer" controls src={data.node.videoUrl}>
                                            Your browser does not support the video element.
                                        </video>
                                    </div>
                                    <div class="mb-4">
                                        <Label for="scriptVideoDisplay" class="mb-2 text-lg">Script (Read-only)</Label>
                                        <Textarea id="scriptVideoDisplay" rows="16" value={data.node.script} readonly class="text-lg"/>
                                    </div>    
                                {/if}
                            {/if}
                        </TabItem>
                        <TabItem open={activeTab === 'menuscript'} title="Menuscript">
                            <div class="mb-4">
                                <Label for="menuscriptHint" class="mb-2 text-lg">Hint</Label>
                                <Textarea id="menuscriptHint" rows="2" bind:value={data.node.menuscriptHint} placeholder="Enter additional hint for generation..." class="text-lg" />
                            </div>
                            <Button on:click={handleGenerateMenuscript} class="text-lg" disabled={menuscriptSpinner}>Update</Button>
                            {#if menuscriptSpinner}
                            <div class='mb-4'>
                                <Spinner />
                            </div>
                            {:else}
                                <div class="mb-4">
                                    <Label for="slideMenuscript" class="mb-2 text-lg">Menuscript ({menuscript_words} words)</Label>
                                    <Textarea id="slideMenuscript" rows="32" bind:value={data.node.menuscript} class="text-lg"/>
                                </div>
                            {/if}
                        </TabItem>
                    </Tabs>
                {:else}
                {/if}
            </div>
        </div>
    </div>
</div>

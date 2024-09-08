<script>
    import axios from 'axios';
    import { Tabs, TabItem, Input, Textarea, Label } from 'flowbite-svelte';
    import { Button } from 'flowbite-svelte';
    import DeckIndex from './DeckIndex.svelte';
    let slideContent = '';
    let hint = '';
    let generationOutput = '';

    function handleGenerate() {
        // Placeholder for generation logic
        generationOutput = 'Generated content will appear here.';
    }
    export let data;

    function updateSlideIndex(slide, slides) {
        let index = -1;
        for (let i = 0; i < slides.length; i++) {
            if (slides[i].id === slide.id) {
                index = i;
                break;
            }
        }
        console.log('Slide index:', index);
        return index;
    }

    $: slideIndex = updateSlideIndex(data.slide, data.slides);

    let leftPanelWidth = 10; // Initial width in percentage

    function handleInsertSlide(event) {
        // Placeholder for add slide logic
        console.log('Add slide clicked', event.detail.slideIndex);
        let index = event.detail.slideIndex;
        let position = null;
        if (index <= 0) {
            position = data.slides[0].position - 1;
        }
        else if (index >= data.slides.length) {
            position = data.slides[data.slides.length - 1].position + 1;
        }
        else {
            position = (data.slides[index - 1].position + data.slides[index].position) / 2;
        }
        axios.post('/api/deck/add_slide/', {
            deck_id: data.deck_id,
            position: position,
        })
        .then(response => {
            let newSlide = response.data;
            data.slides = [...data.slides.slice(0, index), newSlide, ...data.slides.slice(index)];
        })
        .catch(error => {
            console.error('Error adding slide:', error);
        });
    }

    function handleDeleteSlide(event) {
        axios.post('/api/deck/delete_slide/', {
            slide_id: data.slide.id
        })
        .then(response => {
            //data.slides = data.slides.filter(slide => slide.id !== data.slide.id);
        })
        .catch(error => {
            console.error('Error deleting slide:', error);
        });
    }   

    function handleReorderSlide(event) {
        console.log('Reorder slide:', event.detail.oldIndex, event.detail.newIndex);
        let oldIndex = event.detail.oldIndex;
        let newIndex = event.detail.newIndex;
        let slide = data.slides[oldIndex];
        let slides = [
            ...data.slides.slice(0, oldIndex),
            ...data.slides.slice(oldIndex + 1)];
        data.slides = [
            ...slides.slice(0, newIndex),
            slide,
            ...slides.slice(newIndex)
        ];
        for (let i = 0; i < data.slides.length; i++) {
            data.slides[i].index = i;
        }
        data.slides = data.slides;
    }

    function handleDrag(e) {
        const containerWidth = e.target.parentElement.offsetWidth;
        const newWidth = (e.clientX / containerWidth) * 100;
        leftPanelWidth = Math.max(10, Math.min(90, newWidth));
    }

    function handleSave() {
        axios.post('/api/deck/update_slide/', {
            slide_id: data.slide.id,
            content: data.slide.content
        })
        .then(response => {
            let newSlide = response.data;
            data.slides[slideIndex].thumb = newSlide.thumb;
        })
        .catch(error => {
            console.error('Error updating slide:', error);
        });
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
    <DeckIndex deck_id={data.deck_id} slides={data.slides}
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
        </div>
        
        <div class="flex-grow p-4">
            <Tabs>
                <TabItem open title="Outline">
                    <div class="mb-4">
                        <Label for="slideContent" class="mb-2">Slide {slideIndex + 1} Content</Label>
                        <Textarea id="slideContent" rows="4" bind:value={data.slide.content} placeholder="Enter your slide content here..." />
                    </div>
                    <div class="mb-4">
                        <Label for="hint" class="mb-2">Hint</Label>
                        <Input id="hint" type="text" bind:value={hint} placeholder="Enter a hint for generation..." />
                    </div>
                    <Button on:click={handleGenerateScript}>Generate Script</Button>
                </TabItem>
                <TabItem title="Configuration">                    
                </TabItem>
                <TabItem title="Output">
                    <Textarea id="generationOutput" rows="4" bind:value={generationOutput} placeholder="Generated content will appear here..." readonly />
                    <Button on:click={handleGenerateAV}>Generate Audio</Button>
                </TabItem>
            </Tabs>
        </div>
    </div>
</div>



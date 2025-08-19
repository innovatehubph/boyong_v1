// Integration Script for Enhanced Multimedia Chat System
// Seamlessly integrates with existing Pareng Boyong message system

import { multimediaRenderer, enhanceMessage } from './enhanced-multimedia-renderer.js';

// Store original message handler
let originalSetMessage = null;

// Enhanced message system integration
export function initializeEnhancedChat() {
    console.log('🎨 Initializing Enhanced Multimedia Chat System...');
    
    // Get original setMessage function
    if (window.setMessage) {
        originalSetMessage = window.setMessage;
    }
    
    // Override setMessage with enhanced version
    window.setMessage = enhancedSetMessage;
    
    // Add enhanced message event listeners
    setupEnhancedEventListeners();
    
    // Initialize multimedia components
    initializeMultimediaComponents();
    
    // Add enhanced message commands
    registerEnhancedCommands();
    
    console.log('✅ Enhanced Multimedia Chat System initialized successfully!');
}

// Enhanced setMessage function
function enhancedSetMessage(id, type, heading, content, temp, kvps = null) {
    // Search for the existing message container by id
    let messageContainer = document.getElementById(`message-${id}`);
    
    if (messageContainer) {
        // Clear existing content for updates
        messageContainer.innerHTML = "";
    } else {
        // Create a new container if not found
        const sender = type === "user" ? "user" : "ai";
        messageContainer = document.createElement("div");
        messageContainer.id = `message-${id}`;
        messageContainer.classList.add("message-container", `${sender}-container`);
    }
    
    // Try enhanced rendering first
    const wasEnhanced = enhanceMessage(messageContainer, id, type, heading, content, temp, kvps);
    
    if (!wasEnhanced && originalSetMessage) {
        // Fall back to original rendering if content doesn't need enhancement
        return originalSetMessage(id, type, heading, content, temp, kvps);
    } else if (!wasEnhanced) {
        // Basic fallback if no original handler
        const basicContent = document.createElement('div');
        basicContent.className = 'basic-message-content';
        basicContent.textContent = content;
        messageContainer.appendChild(basicContent);
    }
    
    // Add enhanced message to DOM if it's new
    if (!document.getElementById(`message-${id}`)) {
        const chatHistory = document.getElementById("chat-history");
        if (chatHistory) {
            chatHistory.appendChild(messageContainer);
            
            // Auto-scroll to new message
            if (window.getAutoScroll && window.getAutoScroll()) {
                messageContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
        }
    }
    
    // Trigger enhanced processing
    processEnhancedMessage(messageContainer, { id, type, heading, content, temp, kvps });
}

// Setup enhanced event listeners
function setupEnhancedEventListeners() {
    // Listen for multimedia content detection
    document.addEventListener('DOMContentLoaded', () => {
        setupMediaDetection();
        setupDragAndDrop();
        setupKeyboardShortcuts();
    });
    
    // Listen for message updates
    const chatHistory = document.getElementById('chat-history');
    if (chatHistory) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('message-container')) {
                            checkForEnhancedContent(node);
                        }
                    });
                }
            });
        });
        
        observer.observe(chatHistory, { childList: true, subtree: true });
    }
}

// Initialize multimedia components
function initializeMultimediaComponents() {
    // Register custom multimedia message types
    multimediaRenderer.registerComponent('ParengBoyongPlayer', createParengBoyongPlayer);
    multimediaRenderer.registerComponent('FilipinoCulturalContent', createFilipinoCulturalContent);
    multimediaRenderer.registerComponent('InnovateHubShowcase', createInnovateHubShowcase);
    multimediaRenderer.registerComponent('CodeShowcase', createCodeShowcase);
    multimediaRenderer.registerComponent('AIGeneratedContent', createAIGeneratedContent);
    
    // Initialize third-party libraries
    loadEnhancedLibraries();
}

// Custom component creators
function createParengBoyongPlayer(props, children, options) {
    const player = document.createElement('div');
    player.className = 'pareng-boyong-player';
    
    const header = document.createElement('div');
    header.className = 'player-header';
    header.innerHTML = `
        <div class="player-logo">
            <img src="public/innovatehub-logo.png" alt="InnovateHub" width="32" height="32">
            <span>Pareng Boyong Media Player</span>
        </div>
        <div class="player-controls">
            <button class="btn-minimize">−</button>
            <button class="btn-maximize">□</button>
            <button class="btn-close">×</button>
        </div>
    `;
    
    const content = document.createElement('div');
    content.className = 'player-content';
    
    if (props.type === 'video') {
        const video = document.createElement('video');
        video.src = props.src;
        video.controls = true;
        video.poster = props.poster;
        content.appendChild(video);
    } else if (props.type === 'audio') {
        const audio = document.createElement('audio');
        audio.src = props.src;
        audio.controls = true;
        content.appendChild(audio);
    }
    
    player.appendChild(header);
    player.appendChild(content);
    
    // Add Filipino-style player functionality
    addFilipinoPlayerFeatures(player, props);
    
    return player;
}

function createFilipinoCulturalContent(props, children, options) {
    const container = document.createElement('div');
    container.className = 'filipino-cultural-content';
    
    const header = document.createElement('div');
    header.className = 'cultural-header';
    header.innerHTML = `
        <div class="cultural-flag">🇵🇭</div>
        <h3>${props.title || 'Filipino Cultural Content'}</h3>
        <div class="cultural-badge">${props.category || 'Kultura'}</div>
    `;
    
    const content = document.createElement('div');
    content.className = 'cultural-content';
    
    if (props.content) {
        content.innerHTML = props.content;
    }
    
    if (props.media) {
        const mediaContainer = document.createElement('div');
        mediaContainer.className = 'cultural-media';
        
        props.media.forEach(item => {
            if (item.type === 'image') {
                const img = document.createElement('img');
                img.src = item.url;
                img.alt = item.alt || 'Filipino cultural image';
                mediaContainer.appendChild(img);
            } else if (item.type === 'video') {
                const video = document.createElement('video');
                video.src = item.url;
                video.controls = true;
                mediaContainer.appendChild(video);
            }
        });
        
        content.appendChild(mediaContainer);
    }
    
    container.appendChild(header);
    container.appendChild(content);
    
    return container;
}

function createInnovateHubShowcase(props, children, options) {
    const showcase = document.createElement('div');
    showcase.className = 'innovatehub-showcase';
    
    const header = document.createElement('div');
    header.className = 'showcase-header';
    header.innerHTML = `
        <div class="showcase-logo">
            <img src="public/innovatehub-logo.png" alt="InnovateHub" width="48" height="48">
            <div class="showcase-title">
                <h3>InnovateHub PH Showcase</h3>
                <p>Innovation. Technology. Philippines.</p>
            </div>
        </div>
    `;
    
    const content = document.createElement('div');
    content.className = 'showcase-content';
    
    if (props.projects) {
        const projectGrid = document.createElement('div');
        projectGrid.className = 'project-grid';
        
        props.projects.forEach(project => {
            const projectCard = document.createElement('div');
            projectCard.className = 'project-card';
            projectCard.innerHTML = `
                <img src="${project.image}" alt="${project.name}">
                <div class="project-info">
                    <h4>${project.name}</h4>
                    <p>${project.description}</p>
                    <div class="project-tech">${project.tech.join(', ')}</div>
                </div>
            `;
            projectGrid.appendChild(projectCard);
        });
        
        content.appendChild(projectGrid);
    }
    
    showcase.appendChild(header);
    showcase.appendChild(content);
    
    return showcase;
}

function createCodeShowcase(props, children, options) {
    const showcase = document.createElement('div');
    showcase.className = 'code-showcase';
    
    const header = document.createElement('div');
    header.className = 'code-header';
    header.innerHTML = `
        <div class="code-language">${props.language || 'JavaScript'}</div>
        <div class="code-title">${props.title || 'Code Example'}</div>
        <button class="code-copy-btn">Copy</button>
    `;
    
    const codeContainer = document.createElement('div');
    codeContainer.className = 'code-container';
    
    const pre = document.createElement('pre');
    const code = document.createElement('code');
    code.className = `language-${props.language || 'javascript'}`;
    code.textContent = props.code || '';
    
    pre.appendChild(code);
    codeContainer.appendChild(pre);
    
    if (props.output) {
        const output = document.createElement('div');
        output.className = 'code-output';
        output.innerHTML = `
            <div class="output-header">Output:</div>
            <div class="output-content">${props.output}</div>
        `;
        codeContainer.appendChild(output);
    }
    
    showcase.appendChild(header);
    showcase.appendChild(codeContainer);
    
    // Add copy functionality
    const copyBtn = header.querySelector('.code-copy-btn');
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(props.code || '');
        copyBtn.textContent = 'Copied!';
        setTimeout(() => copyBtn.textContent = 'Copy', 2000);
    });
    
    return showcase;
}

function createAIGeneratedContent(props, children, options) {
    const container = document.createElement('div');
    container.className = 'ai-generated-content';
    
    const header = document.createElement('div');
    header.className = 'ai-header';
    header.innerHTML = `
        <div class="ai-badge">
            <span class="ai-icon">🤖</span>
            <span>AI Generated by Pareng Boyong</span>
        </div>
        <div class="ai-timestamp">${new Date().toLocaleString()}</div>
    `;
    
    const content = document.createElement('div');
    content.className = 'ai-content';
    
    if (props.type === 'image' && props.src) {
        const img = document.createElement('img');
        img.src = props.src;
        img.alt = props.alt || 'AI Generated Image';
        img.className = 'ai-generated-image';
        content.appendChild(img);
    } else if (props.type === 'video' && props.src) {
        const video = document.createElement('video');
        video.src = props.src;
        video.controls = true;
        video.className = 'ai-generated-video';
        content.appendChild(video);
    } else if (props.type === 'audio' && props.src) {
        const audio = document.createElement('audio');
        audio.src = props.src;
        audio.controls = true;
        audio.className = 'ai-generated-audio';
        content.appendChild(audio);
    }
    
    if (props.description) {
        const desc = document.createElement('div');
        desc.className = 'ai-description';
        desc.textContent = props.description;
        content.appendChild(desc);
    }
    
    container.appendChild(header);
    container.appendChild(content);
    
    return container;
}

// Setup media detection for incoming messages
function setupMediaDetection() {
    // Auto-detect media URLs in text content
    const urlRegex = /(https?:\/\/[^\s]+\.(jpg|jpeg|png|gif|webp|svg|mp4|webm|mov|avi|mp3|wav|ogg|m4a|flac))/gi;
    
    // Monitor for new messages and enhance them
    const chatHistory = document.getElementById('chat-history');
    if (chatHistory) {
        chatHistory.addEventListener('DOMNodeInserted', (event) => {
            const node = event.target;
            if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('message-container')) {
                setTimeout(() => checkForMediaContent(node), 100);
            }
        });
    }
}

function checkForMediaContent(messageContainer) {
    const textContent = messageContainer.textContent || '';
    const urlRegex = /(https?:\/\/[^\s]+\.(jpg|jpeg|png|gif|webp|svg|mp4|webm|mov|avi|mp3|wav|ogg|m4a|flac))/gi;
    const matches = textContent.match(urlRegex);
    
    if (matches) {
        matches.forEach(url => {
            const mediaType = multimediaRenderer.detectMediaType(url);
            const mediaContainer = document.createElement('div');
            mediaContainer.className = 'auto-detected-media';
            
            multimediaRenderer.renderMultimediaContent(mediaContainer, { url, type: mediaType }, {});
            messageContainer.appendChild(mediaContainer);
        });
    }
}

// Setup drag and drop for multimedia files
function setupDragAndDrop() {
    const chatHistory = document.getElementById('chat-history');
    if (!chatHistory) return;
    
    chatHistory.addEventListener('dragover', (e) => {
        e.preventDefault();
        chatHistory.classList.add('drag-over');
    });
    
    chatHistory.addEventListener('dragleave', (e) => {
        e.preventDefault();
        chatHistory.classList.remove('drag-over');
    });
    
    chatHistory.addEventListener('drop', (e) => {
        e.preventDefault();
        chatHistory.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files);
        files.forEach(file => handleDroppedFile(file));
    });
}

function handleDroppedFile(file) {
    const supportedTypes = ['image/', 'video/', 'audio/'];
    const isSupported = supportedTypes.some(type => file.type.startsWith(type));
    
    if (!isSupported) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        const dataUrl = e.target.result;
        const messageId = 'dropped-' + Date.now();
        const mediaType = file.type.startsWith('image/') ? 'image' : 
                         file.type.startsWith('video/') ? 'video' : 'audio';
        
        // Create dropped file message
        window.setMessage(messageId, 'user', 'Dropped File', {
            type: 'multimedia',
            url: dataUrl,
            mediaType: mediaType,
            filename: file.name,
            size: file.size
        }, false);
    };
    
    reader.readAsDataURL(file);
}

// Setup keyboard shortcuts for enhanced features
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Shift + M: Toggle multimedia mode
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'M') {
            e.preventDefault();
            toggleMultimediaMode();
        }
        
        // Ctrl/Cmd + Shift + I: Insert multimedia component
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'I') {
            e.preventDefault();
            showMultimediaInsertDialog();
        }
    });
}

// Load enhanced libraries
function loadEnhancedLibraries() {
    // Load additional libraries as needed
    const libraries = [
        { name: 'Prism', url: 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js', css: 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css' },
        { name: 'Chart.js', url: 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js' },
        { name: 'Leaflet', url: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js', css: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css' }
    ];
    
    libraries.forEach(lib => {
        if (lib.css && !document.querySelector(`link[href*="${lib.name.toLowerCase()}"]`)) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = lib.css;
            document.head.appendChild(link);
        }
        
        if (!window[lib.name] && !document.querySelector(`script[src*="${lib.name.toLowerCase()}"]`)) {
            const script = document.createElement('script');
            script.src = lib.url;
            script.async = true;
            document.head.appendChild(script);
        }
    });
}

// Enhanced message processing
function processEnhancedMessage(container, metadata) {
    // Add message metadata
    container.dataset.messageId = metadata.id;
    container.dataset.messageType = metadata.type;
    
    // Add enhanced interactions
    addMessageInteractions(container);
    
    // Add accessibility features
    addAccessibilityFeatures(container);
    
    // Add animation effects
    addAnimationEffects(container);
}

function addMessageInteractions(container) {
    // Add right-click context menu for enhanced messages
    container.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showEnhancedContextMenu(e, container);
    });
    
    // Add double-click to expand/collapse
    container.addEventListener('dblclick', () => {
        container.classList.toggle('expanded');
    });
}

function addAccessibilityFeatures(container) {
    // Add ARIA labels
    container.setAttribute('role', 'article');
    container.setAttribute('aria-label', 'Enhanced message');
    
    // Add keyboard navigation
    container.setAttribute('tabindex', '0');
    container.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            container.click();
        }
    });
}

function addAnimationEffects(container) {
    // Add entrance animation
    container.style.opacity = '0';
    container.style.transform = 'translateY(20px)';
    
    requestAnimationFrame(() => {
        container.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        container.style.opacity = '1';
        container.style.transform = 'translateY(0)';
    });
}

// Enhanced context menu
function showEnhancedContextMenu(event, container) {
    const menu = document.createElement('div');
    menu.className = 'enhanced-context-menu';
    menu.innerHTML = `
        <div class="menu-item" data-action="copy">Copy Content</div>
        <div class="menu-item" data-action="save">Save Media</div>
        <div class="menu-item" data-action="share">Share Message</div>
        <div class="menu-item" data-action="enhance">Enhance Further</div>
        <div class="menu-separator"></div>
        <div class="menu-item" data-action="report">Report Issue</div>
    `;
    
    menu.style.position = 'fixed';
    menu.style.left = event.clientX + 'px';
    menu.style.top = event.clientY + 'px';
    menu.style.zIndex = '10000';
    
    document.body.appendChild(menu);
    
    // Handle menu actions
    menu.addEventListener('click', (e) => {
        const action = e.target.dataset.action;
        if (action) {
            handleContextMenuAction(action, container);
        }
        document.body.removeChild(menu);
    });
    
    // Remove menu on outside click
    setTimeout(() => {
        document.addEventListener('click', () => {
            if (menu.parentNode) {
                document.body.removeChild(menu);
            }
        }, { once: true });
    }, 10);
}

function handleContextMenuAction(action, container) {
    switch (action) {
        case 'copy':
            copyMessageContent(container);
            break;
        case 'save':
            saveMessageMedia(container);
            break;
        case 'share':
            shareMessage(container);
            break;
        case 'enhance':
            enhanceMessageFurther(container);
            break;
        case 'report':
            reportMessageIssue(container);
            break;
    }
}

// Utility functions
function toggleMultimediaMode() {
    document.body.classList.toggle('multimedia-mode');
    console.log('Multimedia mode toggled');
}

function showMultimediaInsertDialog() {
    // Show dialog for inserting multimedia content
    console.log('Multimedia insert dialog shown');
}

function copyMessageContent(container) {
    const text = container.textContent || '';
    navigator.clipboard.writeText(text);
    showToast('Content copied to clipboard');
}

function saveMessageMedia(container) {
    const media = container.querySelectorAll('img, video, audio');
    media.forEach(element => {
        const link = document.createElement('a');
        link.href = element.src;
        link.download = element.alt || 'media';
        link.click();
    });
}

function shareMessage(container) {
    if (navigator.share) {
        navigator.share({
            title: 'Pareng Boyong Message',
            text: container.textContent || '',
            url: window.location.href
        });
    }
}

function enhanceMessageFurther(container) {
    // Add more enhancement options
    console.log('Further enhancement requested');
}

function reportMessageIssue(container) {
    // Report message issues
    console.log('Message issue reported');
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'enhanced-toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, rgba(0, 255, 255, 0.9), rgba(255, 0, 128, 0.9));
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10000;
        animation: toastSlideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'toastSlideOut 0.3s ease';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

function checkForEnhancedContent(container) {
    const content = container.textContent || '';
    
    // Check for various content types that could be enhanced
    if (content.includes('```') || content.includes('<html>') || content.includes('http')) {
        // Re-process with enhanced renderer
        const messageId = container.id.replace('message-', '');
        setTimeout(() => {
            multimediaRenderer.postProcessMessage(container, { id: messageId });
        }, 100);
    }
}

// Register enhanced commands
function registerEnhancedCommands() {
    // Register commands that can trigger enhanced rendering
    const enhancedCommands = [
        '/image', '/video', '/audio', '/gallery', '/chart', '/map', '/code', '/showcase'
    ];
    
    // These would integrate with the existing command system
    enhancedCommands.forEach(command => {
        console.log(`Enhanced command registered: ${command}`);
    });
}

function addFilipinoPlayerFeatures(player, props) {
    // Add Filipino-specific features to media players
    const controls = player.querySelector('.player-controls');
    
    // Add subtitle support for Filipino content
    if (props.subtitles) {
        const subtitleBtn = document.createElement('button');
        subtitleBtn.textContent = 'CC';
        subtitleBtn.className = 'subtitle-toggle';
        subtitleBtn.addEventListener('click', () => {
            // Toggle Filipino subtitles
            console.log('Filipino subtitles toggled');
        });
        controls.insertBefore(subtitleBtn, controls.firstChild);
    }
    
    // Add speed control for Filipino learners
    const speedBtn = document.createElement('button');
    speedBtn.textContent = '1x';
    speedBtn.className = 'speed-control';
    speedBtn.addEventListener('click', () => {
        // Cycle through speeds: 0.5x, 0.75x, 1x, 1.25x, 1.5x
        console.log('Playback speed changed');
    });
    controls.insertBefore(speedBtn, controls.firstChild);
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedChat);
} else {
    initializeEnhancedChat();
}

// Export for external use
export { initializeEnhancedChat, multimediaRenderer };
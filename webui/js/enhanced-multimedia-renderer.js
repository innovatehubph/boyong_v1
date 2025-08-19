/**
 * Enhanced Multimedia Renderer for Pareng Boyong
 * Extends the existing message rendering system to support video, audio, and enhanced images
 */

// Export functions to be used by messages.js
export { 
  convertMultimediaTags, 
  renderMultimediaContent, 
  createMediaPlayer,
  enhanceImageRendering 
};

/**
 * Convert multimedia tags to HTML media elements
 * Supports: <image>, <video>, <audio>, <media>
 */
function convertMultimediaTags(content) {
  // Handle existing image tags (preserve compatibility)
  content = convertImageTags(content);
  
  // Handle video tags: <video>base64content</video>
  content = convertVideoTags(content);
  
  // Handle audio tags: <audio>base64content</audio>
  content = convertAudioTags(content);
  
  // Handle generic media tags: <media type="video|audio|image">base64content</media>
  content = convertMediaTags(content);
  
  return content;
}

/**
 * Convert <image> tags with enhanced styling and modal support
 */
function convertImageTags(content) {
  const imageTagRegex = /<image>(.*?)<\/image>/g;
  
  return content.replace(imageTagRegex, (match, base64Content) => {
    const imageId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return `
      <div class="multimedia-container image-container">
        <img 
          id="${imageId}"
          src="data:image/jpeg;base64,${base64Content}" 
          alt="Generated Image" 
          class="multimedia-image clickable-image"
          style="max-width: 100%; height: auto; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"
          onclick="openImageModal(this.src, 1000)"
          loading="lazy"
        />
        <div class="multimedia-controls">
          <button onclick="downloadMedia('${imageId}', 'image', 'generated-image.jpg')" class="media-download-btn">
            <span class="material-symbols-outlined">download</span>
          </button>
        </div>
      </div>
    `;
  });
}

/**
 * Convert <video> tags to HTML5 video elements
 */
function convertVideoTags(content) {
  const videoTagRegex = /<video>(.*?)<\/video>/g;
  
  return content.replace(videoTagRegex, (match, base64Content) => {
    const videoId = `vid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return `
      <div class="multimedia-container video-container">
        <video 
          id="${videoId}"
          class="multimedia-video"
          controls 
          preload="metadata"
          style="width: 100%; max-width: 500px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"
        >
          <source src="data:video/mp4;base64,${base64Content}" type="video/mp4">
          Your browser does not support the video tag.
        </video>
        <div class="multimedia-controls">
          <button onclick="downloadMedia('${videoId}', 'video', 'generated-video.mp4')" class="media-download-btn">
            <span class="material-symbols-outlined">download</span>
          </button>
          <button onclick="toggleFullscreen('${videoId}')" class="media-fullscreen-btn">
            <span class="material-symbols-outlined">fullscreen</span>
          </button>
        </div>
      </div>
    `;
  });
}

/**
 * Convert <audio> tags to HTML5 audio elements
 */
function convertAudioTags(content) {
  const audioTagRegex = /<audio>(.*?)<\/audio>/g;
  
  return content.replace(audioTagRegex, (match, base64Content) => {
    const audioId = `aud_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    return `
      <div class="multimedia-container audio-container">
        <audio 
          id="${audioId}"
          class="multimedia-audio"
          controls 
          preload="metadata"
          style="width: 100%; max-width: 400px; border-radius: 8px;"
        >
          <source src="data:audio/wav;base64,${base64Content}" type="audio/wav">
          <source src="data:audio/mp3;base64,${base64Content}" type="audio/mp3">
          Your browser does not support the audio tag.
        </audio>
        <div class="multimedia-controls">
          <button onclick="downloadMedia('${audioId}', 'audio', 'generated-audio.wav')" class="media-download-btn">
            <span class="material-symbols-outlined">download</span>
          </button>
        </div>
      </div>
    `;
  });
}

/**
 * Convert <media> tags with type attribute
 */
function convertMediaTags(content) {
  const mediaTagRegex = /<media\s+type=["']?(video|audio|image)["']?>(.*?)<\/media>/g;
  
  return content.replace(mediaTagRegex, (match, mediaType, base64Content) => {
    switch (mediaType.toLowerCase()) {
      case 'image':
        return `<image>${base64Content}</image>`;
      case 'video':
        return `<video>${base64Content}</video>`;
      case 'audio':
        return `<audio>${base64Content}</audio>`;
      default:
        return match; // Return original if unknown type
    }
  });
}

/**
 * Create a multimedia player for various content types
 */
function createMediaPlayer(mediaType, content, options = {}) {
  const {
    width = '100%',
    height = 'auto',
    controls = true,
    autoplay = false,
    loop = false,
    className = ''
  } = options;
  
  const mediaId = `media_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  switch (mediaType.toLowerCase()) {
    case 'image':
      return `
        <div class="multimedia-container ${className}">
          <img 
            id="${mediaId}"
            src="data:image/jpeg;base64,${content}"
            alt="Generated Image"
            class="multimedia-image"
            style="width: ${width}; height: ${height}; border-radius: 8px; cursor: pointer;"
            onclick="openImageModal(this.src, 1000)"
          />
        </div>
      `;
      
    case 'video':
      return `
        <div class="multimedia-container ${className}">
          <video 
            id="${mediaId}"
            class="multimedia-video"
            ${controls ? 'controls' : ''}
            ${autoplay ? 'autoplay' : ''}
            ${loop ? 'loop' : ''}
            style="width: ${width}; height: ${height}; border-radius: 8px;"
          >
            <source src="data:video/mp4;base64,${content}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
        </div>
      `;
      
    case 'audio':
      return `
        <div class="multimedia-container ${className}">
          <audio 
            id="${mediaId}"
            class="multimedia-audio"
            ${controls ? 'controls' : ''}
            ${autoplay ? 'autoplay' : ''}
            ${loop ? 'loop' : ''}
            style="width: ${width}; border-radius: 8px;"
          >
            <source src="data:audio/wav;base64,${content}" type="audio/wav">
            <source src="data:audio/mp3;base64,${content}" type="audio/mp3">
            Your browser does not support the audio tag.
          </audio>
        </div>
      `;
      
    default:
      return `<div class="multimedia-error">Unsupported media type: ${mediaType}</div>`;
  }
}

/**
 * Render multimedia content directly in message containers
 */
function renderMultimediaContent(container, mediaData) {
  if (!mediaData || !mediaData.type || !mediaData.content) {
    return;
  }
  
  const mediaElement = createMediaPlayer(mediaData.type, mediaData.content, mediaData.options || {});
  const mediaContainer = document.createElement('div');
  mediaContainer.innerHTML = mediaElement;
  
  container.appendChild(mediaContainer);
}

/**
 * Enhanced image rendering with progressive loading and optimization
 */
function enhanceImageRendering(imageElement) {
  // Add loading animation
  imageElement.style.opacity = '0';
  imageElement.style.transition = 'opacity 0.3s ease';
  
  // Add load event listener
  imageElement.addEventListener('load', function() {
    this.style.opacity = '1';
  });
  
  // Add error handling
  imageElement.addEventListener('error', function() {
    this.src = '/public/image-error.svg';
    this.alt = 'Failed to load image';
  });
  
  // Add intersection observer for lazy loading
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imageObserver.unobserve(img);
        }
      });
    });
    
    imageObserver.observe(imageElement);
  }
}

// Global utility functions for media controls
window.downloadMedia = function(elementId, mediaType, filename) {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  let dataUrl;
  
  if (mediaType === 'image') {
    dataUrl = element.src;
  } else if (mediaType === 'video' || mediaType === 'audio') {
    dataUrl = element.querySelector('source').src;
  }
  
  if (dataUrl) {
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

window.toggleFullscreen = function(elementId) {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  if (element.requestFullscreen) {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      element.requestFullscreen();
    }
  }
};

window.openImageModal = function(src, maxWidth = 1000) {
  // Create modal overlay
  const modal = document.createElement('div');
  modal.className = 'image-modal-overlay';
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    backdrop-filter: blur(5px);
  `;
  
  // Create modal image
  const modalImage = document.createElement('img');
  modalImage.src = src;
  modalImage.style.cssText = `
    max-width: 90vw;
    max-height: 90vh;
    border-radius: 8px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  `;
  
  modal.appendChild(modalImage);
  document.body.appendChild(modal);
  
  // Close modal on click
  modal.addEventListener('click', function() {
    document.body.removeChild(modal);
  });
  
  // Close modal on escape
  const escapeHandler = function(e) {
    if (e.key === 'Escape') {
      document.body.removeChild(modal);
      document.removeEventListener('keydown', escapeHandler);
    }
  };
  document.addEventListener('keydown', escapeHandler);
};
/**
 * Enhanced File Browser for Pareng Boyong with Full VPS Access
 * Extends existing file browser functionality to provide VPS-wide navigation
 */

// Enhanced file browser proxy with VPS navigation
const enhancedFileBrowserProxy = {
  ...window.fileBrowserModalProxy, // Extend existing functionality
  
  // VPS Navigation roots
  navigationRoots: {
    "$WORK_DIR": "/",  // Full VPS access
    "$VPS_ROOT": "/",
    "$VPS_WWW": "/var/www", 
    "$VPS_ROOT_HOME": "/root",
    "$VPS_TMP": "/tmp",
    "$PROJECTS": "/root/projects/pareng-boyong/pareng-boyong-projects",
    "$DELIVERABLES": "/root/projects/pareng-boyong/pareng_boyong_deliverables",
    "$WEBAPPS": "/var/www"
  },
  
  // Current VPS access mode
  vpsMode: false,
  
  // Quick navigation history
  bookmarks: [],
  
  async openModal(path, vpsMode = false) {
    const modalEl = document.getElementById("fileBrowserModal");
    const modalAD = Alpine.$data(modalEl);

    modalAD.isOpen = true;
    modalAD.isLoading = true;
    modalAD.history = [];
    modalAD.vpsMode = vpsMode;

    // Initialize currentPath based on mode
    if (path) {
      modalAD.browser.currentPath = path;
    } else if (vpsMode) {
      modalAD.browser.currentPath = "/";
    } else if (!modalAD.browser.currentPath) {
      modalAD.browser.currentPath = "/";  // Start at VPS root
    }

    await modalAD.fetchFiles(modalAD.browser.currentPath);
  },

  async fetchFiles(path = "") {
    this.isLoading = true;
    try {
      // Use enhanced API endpoint for better VPS access
      const response = await fetchApi(
        `/get_work_dir_files?path=${encodeURIComponent(path)}`
      );

      if (response.ok) {
        const data = await response.json();
        this.browser.entries = data.data.entries;
        this.browser.currentPath = data.data.current_path;
        this.browser.parentPath = data.data.parent_path;
        
        // Store navigation roots if available
        if (data.data.navigation_roots) {
          this.navigationRoots = data.data.navigation_roots;
        }
      } else {
        console.error("Error fetching files:", await response.text());
        this.browser.entries = [];
      }
    } catch (error) {
      window.toastFetchError("Error fetching files", error);
      this.browser.entries = [];
    } finally {
      this.isLoading = false;
    }
  },

  async navigateToRoot(rootAlias) {
    const rootPath = this.navigationRoots[rootAlias] || rootAlias;
    await this.navigateToFolder(rootPath);
  },

  async navigateToVpsRoot() {
    await this.navigateToFolder("/");
  },

  async navigateToHome() {
    await this.navigateToFolder("/root");
  },

  async navigateToWebApps() {
    await this.navigateToFolder("/var/www");
  },

  async navigateToTmp() {
    await this.navigateToFolder("/tmp");
  },

  async navigateToA0() {
    await this.navigateToFolder("/a0");
  },

  async navigateToProjects() {
    await this.navigateToFolder("/root/projects/pareng-boyong/pareng-boyong-projects");
  },

  async navigateToDeliverables() {
    await this.navigateToFolder("/root/projects/pareng-boyong/pareng_boyong_deliverables");
  },

  addBookmark(path, name) {
    const bookmark = {
      name: name || path.split('/').pop() || 'Root',
      path: path,
      timestamp: Date.now()
    };
    
    // Avoid duplicates
    this.bookmarks = this.bookmarks.filter(b => b.path !== path);
    this.bookmarks.unshift(bookmark);
    
    // Keep only last 10 bookmarks
    this.bookmarks = this.bookmarks.slice(0, 10);
    
    // Save to localStorage
    localStorage.setItem('parengBoyong_fileBookmarks', JSON.stringify(this.bookmarks));
  },

  loadBookmarks() {
    try {
      const saved = localStorage.getItem('parengBoyong_fileBookmarks');
      if (saved) {
        this.bookmarks = JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Failed to load bookmarks:', e);
      this.bookmarks = [];
    }
  },

  async navigateToBookmark(bookmark) {
    await this.navigateToFolder(bookmark.path);
  },

  removeBookmark(bookmark) {
    this.bookmarks = this.bookmarks.filter(b => b.path !== bookmark.path);
    localStorage.setItem('parengBoyong_fileBookmarks', JSON.stringify(this.bookmarks));
  },

  getFileIcon(entry) {
    if (entry.is_dir) {
      if (entry.protected) {
        return 'lock';
      }
      return 'folder';
    }
    
    switch (entry.type) {
      case 'image': return 'image';
      case 'code': return 'code';
      case 'document': return 'description';
      case 'config': return 'settings';
      case 'archive': return 'folder_zip';
      case 'video': return 'movie';
      case 'audio': return 'audio_file';
      default: return 'draft';
    }
  },

  getPathBreadcrumbs() {
    if (!this.browser.currentPath) return [];
    
    const parts = this.browser.currentPath.split('/').filter(Boolean);
    const breadcrumbs = [{name: 'Root', path: '/'}];
    
    let currentPath = '';
    for (const part of parts) {
      currentPath += '/' + part;
      breadcrumbs.push({
        name: part,
        path: currentPath
      });
    }
    
    return breadcrumbs;
  },

  async navigateToBreadcrumb(breadcrumb) {
    await this.navigateToFolder(breadcrumb.path);
  },

  formatFileSize(size) {
    if (size === 0) return "0 Bytes";
    
    // If it's a directory, show item count
    if (typeof size === 'number' && size < 1024) {
      return `${size} items`;
    }
    
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(size) / Math.log(k));
    return parseFloat((size / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  },

  isProtectedPath(path) {
    const protectedPaths = ['/etc', '/usr', '/var/lib', '/var/log', '/opt'];
    return protectedPaths.some(p => path.startsWith(p));
  },

  showProtectionWarning(path) {
    return confirm(
      `⚠️ Warning: You are accessing a protected system directory:\n${path}\n\n` +
      `Please be careful when making changes to system files.\n\n` +
      `Continue?`
    );
  },

  async navigateToFolder(path) {
    // Check if this is a protected path and show warning
    if (this.isProtectedPath(path)) {
      if (!this.showProtectionWarning(path)) {
        return;
      }
    }
    
    // Push current path to history before navigating
    if (this.browser.currentPath !== path) {
      this.history.push(this.browser.currentPath);
    }
    
    await this.fetchFiles(path);
  }
};

// Initialize enhanced file browser
document.addEventListener("alpine:init", () => {
  Alpine.data("enhancedFileBrowserProxy", () => ({
    init() {
      Object.assign(this, enhancedFileBrowserProxy);
      
      // Load bookmarks on initialization
      this.loadBookmarks();
      
      // Ensure immediate file fetch when modal opens
      this.$watch("isOpen", async (value) => {
        if (value) {
          await this.fetchFiles(this.browser.currentPath);
        }
      });
    },
  }));
});

// Global functions for VPS file browser
window.openVpsFileBrowser = function(path = "/") {
  enhancedFileBrowserProxy.openModal(path, true);
};

window.openA0FileBrowser = function() {
  enhancedFileBrowserProxy.openModal("/a0", false);
};

window.openProjectsBrowser = function() {
  enhancedFileBrowserProxy.openModal("/root/projects/pareng-boyong/pareng-boyong-projects", false);
};

// Enhanced file link handler with VPS support
window.openEnhancedFileLink = async function (path) {
  try {
    const resp = await window.sendJsonData("/file_info", { path });
    if (!resp.exists) {
      window.toast("File does not exist.", "error");
      return;
    }

    if (resp.is_dir) {
      enhancedFileBrowserProxy.openModal(resp.abs_path, true);
    } else {
      enhancedFileBrowserProxy.downloadFile({
        path: resp.abs_path,
        name: resp.file_name,
      });
    }
  } catch (e) {
    window.toastFetchError("Error opening file", e);
  }
};

// Export enhanced proxy
window.enhancedFileBrowserProxy = enhancedFileBrowserProxy;
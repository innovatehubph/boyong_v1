const fileBrowserModalProxy = {
  isOpen: false,
  isLoading: false,
  initialized: false,
  errorMessage: "",

  browser: {
    title: "File Browser",
    currentPath: "/a0",
    entries: [],
    parentPath: "",
    sortBy: "name",
    sortDirection: "asc",
  },

  // Initialize navigation history
  history: [],

  async openModal(path) {
    console.log("File browser modal opening...", path);
    
    try {
      // Initialize modal state
      this.errorMessage = "";
      this.isOpen = true;
      this.isLoading = true;
      this.history = [];
      this.browser.entries = [];
      this.browser.title = "File Browser - Loading...";
      
      // Set path
      const targetPath = path || this.browser.currentPath || "/a0";
      this.browser.currentPath = targetPath;
      
      console.log("Modal state set, fetching files for:", targetPath);
      
      // Force UI update for Alpine
      if (typeof Alpine !== 'undefined') {
        Alpine.nextTick(() => {
          console.log("Alpine nextTick executed");
        });
      }
      
      // Small delay for UI to update
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Fetch files
      await this.fetchFiles(targetPath);
      this.browser.title = "File Browser";
      
      // Try Alpine if available
      try {
        const modalEl = document.getElementById("fileBrowserModal");
        if (modalEl && typeof Alpine !== 'undefined') {
          const modalAD = Alpine.$data(modalEl);
          if (modalAD) {
            // Sync state with Alpine
            Object.assign(modalAD, this);
          }
        }
      } catch (alpineError) {
        console.log("Alpine sync skipped:", alpineError.message);
      }
      
    } catch (error) {
      console.error("Error opening file browser modal:", error);
      this.errorMessage = "Error: " + error.message;
      this.isLoading = false;
      
      // Simple fallback alert for mobile
      if (window.innerWidth <= 768) {
        alert("Error opening file browser. Please try again.");
      }
    }
  },

  isArchive(filename) {
    const archiveExts = ["zip", "tar", "gz", "rar", "7z"];
    const ext = filename.split(".").pop().toLowerCase();
    return archiveExts.includes(ext);
  },

  async fetchFiles(path = "") {
    console.log("Fetching files for path:", path);
    this.isLoading = true;
    this.errorMessage = "";
    this.browser.entries = [];
    
    try {
      // Convert $WORK_DIR to actual path
      if (!path || path === "$WORK_DIR" || path === "") {
        path = "/a0";
      }
      
      const url = `/get_work_dir_files?path=${encodeURIComponent(path)}`;
      console.log("Fetching from URL:", url);
      
      // Use native fetch for better mobile compatibility
      let response;
      if (typeof fetchApi !== 'undefined') {
        response = await fetchApi(url);
      } else {
        // Fallback to native fetch
        response = await fetch(url, {
          method: 'GET',
          credentials: 'same-origin',
          headers: {
            'Accept': 'application/json',
          }
        });
      }
      
      console.log("Response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("Files data received, entries:", data?.data?.entries?.length || 0);
        
        // Validate data structure
        if (data && data.data && Array.isArray(data.data.entries)) {
          this.browser.entries = data.data.entries;
          this.browser.currentPath = data.data.current_path || path;
          this.browser.parentPath = data.data.parent_path || "";
          
          console.log("Files loaded:", this.browser.entries.length, "entries");
          this.errorMessage = "";
        } else {
          console.error("Invalid data structure");
          this.browser.entries = [];
          this.errorMessage = "Invalid data received from server";
        }
      } else {
        console.error("HTTP Error:", response.status);
        this.browser.entries = [];
        this.errorMessage = `Error loading files (${response.status})`;
      }
    } catch (error) {
      console.error("Exception in fetchFiles:", error.message);
      this.browser.entries = [];
      this.errorMessage = "Failed to load files: " + error.message;
      
      // Don't show alert on mobile - use error message display instead
      if (window.innerWidth > 768) {
        window.toastFetchError && window.toastFetchError("Error fetching files", error);
      }
    } finally {
      this.isLoading = false;
      this.initialized = true;
      console.log("fetchFiles completed");
    }
  },

  async navigateToFolder(path) {
    // Push current path to history before navigating
    if (this.browser.currentPath !== path) {
      this.history.push(this.browser.currentPath);
    }
    await this.fetchFiles(path);
  },

  async navigateUp() {
    if (this.browser.parentPath !== "") {
      // Push current path to history before navigating up
      this.history.push(this.browser.currentPath);
      await this.fetchFiles(this.browser.parentPath);
    }
  },

  sortFiles(entries) {
    return [...entries].sort((a, b) => {
      // Folders always come first
      if (a.is_dir !== b.is_dir) {
        return a.is_dir ? -1 : 1;
      }

      const direction = this.browser.sortDirection === "asc" ? 1 : -1;
      switch (this.browser.sortBy) {
        case "name":
          return direction * a.name.localeCompare(b.name);
        case "size":
          return direction * (a.size - b.size);
        case "date":
          return direction * (new Date(a.modified) - new Date(b.modified));
        default:
          return 0;
      }
    });
  },

  toggleSort(column) {
    if (this.browser.sortBy === column) {
      this.browser.sortDirection =
        this.browser.sortDirection === "asc" ? "desc" : "asc";
    } else {
      this.browser.sortBy = column;
      this.browser.sortDirection = "asc";
    }
  },

  async deleteFile(file) {
    if (!confirm(`Are you sure you want to delete ${file.name}?`)) {
      return;
    }

    try {
      const response = await fetchApi("/delete_work_dir_file", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          path: file.path,
          currentPath: this.browser.currentPath,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        this.browser.entries = this.browser.entries.filter(
          (entry) => entry.path !== file.path
        );
        alert("File deleted successfully.");
      } else {
        alert(`Error deleting file: ${await response.text()}`);
      }
    } catch (error) {
      window.toastFetchError("Error deleting file", error);
      alert("Error deleting file");
    }
  },

  async handleFileUpload(event) {
    try {
      const files = event.target.files;
      if (!files.length) return;

      const formData = new FormData();
      formData.append("path", this.browser.currentPath);

      for (let i = 0; i < files.length; i++) {
        const ext = files[i].name.split(".").pop().toLowerCase();
        if (!["zip", "tar", "gz", "rar", "7z"].includes(ext)) {
          if (files[i].size > 100 * 1024 * 1024) {
            // 100MB
            alert(
              `File ${files[i].name} exceeds the maximum allowed size of 100MB.`
            );
            continue;
          }
        }
        formData.append("files[]", files[i]);
      }

      // Proceed with upload after validation
      const response = await fetchApi("/upload_work_dir_files", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Update the file list with new data
        this.browser.entries = data.data.entries.map((entry) => ({
          ...entry,
          uploadStatus: data.failed.includes(entry.name) ? "failed" : "success",
        }));
        this.browser.currentPath = data.data.current_path;
        this.browser.parentPath = data.data.parent_path;

        // Show success message
        if (data.failed && data.failed.length > 0) {
          const failedFiles = data.failed
            .map((file) => `${file.name}: ${file.error}`)
            .join("\n");
          alert(`Some files failed to upload:\n${failedFiles}`);
        }
      } else {
        alert(data.message);
      }
    } catch (error) {
      window.toastFetchError("Error uploading files", error);
      alert("Error uploading files");
    }
  },

  async downloadFile(file) {
    try {
      const downloadUrl = `/download_work_dir_file?path=${encodeURIComponent(
        file.path
      )}`;

      const response = await fetchApi(downloadUrl);

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const blob = await response.blob();

      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(link.href);
    } catch (error) {
      window.toastFetchError("Error downloading file", error);
      alert("Error downloading file");
    }
  },

  // Helper Functions
  formatFileSize(size) {
    if (size === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(size) / Math.log(k));
    return parseFloat((size / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  },

  formatDate(dateString) {
    const options = {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  },

  handleClose() {
    this.isOpen = false;
  },
};

// Initialize Alpine data - mobile compatible approach
if (typeof Alpine !== 'undefined') {
  // Wait for Alpine to be ready
  document.addEventListener("alpine:init", () => {
    Alpine.data("fileBrowserModalProxy", () => ({
      ...fileBrowserModalProxy,
      init() {
        console.log("Alpine fileBrowserModalProxy initialized");
        // Copy all properties and methods
        Object.keys(fileBrowserModalProxy).forEach(key => {
          if (typeof fileBrowserModalProxy[key] === 'function') {
            this[key] = fileBrowserModalProxy[key].bind(this);
          } else {
            this[key] = fileBrowserModalProxy[key];
          }
        });
        
        // Initialize browser data if not set
        if (!this.browser.title) {
          this.browser.title = "File Browser";
        }
        if (!this.browser.currentPath) {
          this.browser.currentPath = "/a0";
        }
        if (!this.browser.entries) {
          this.browser.entries = [];
        }
        
        // Watch for modal open
        this.$watch("isOpen", async (value) => {
          console.log("Modal isOpen changed to:", value);
          if (value && !this.initialized) {
            await this.fetchFiles(this.browser.currentPath || "/a0");
          }
        });
      },
    }));
  });
  
  // Also try to initialize immediately if Alpine is already ready
  if (Alpine.version) {
    console.log("Alpine already initialized, setting up data");
    Alpine.data("fileBrowserModalProxy", () => ({
      ...fileBrowserModalProxy,
      init() {
        Object.assign(this, fileBrowserModalProxy);
      }
    }));
  }
} else {
  console.warn("Alpine.js not found - file browser will use fallback mode");
}

// Keep the global assignment for backward compatibility and mobile
window.fileBrowserModalProxy = fileBrowserModalProxy;

// Add a global function to test file browser opening
window.testFileBrowser = function() {
  console.log("Testing file browser...");
  console.log("fileBrowserModalProxy:", window.fileBrowserModalProxy);
  
  try {
    window.fileBrowserModalProxy.openModal();
  } catch (error) {
    console.error("Error testing file browser:", error);
  }
};

// Enhanced mobile and iPhone compatibility
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM loaded, setting up file browser with iPhone support...");
  
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isMobile = window.innerWidth <= 768 || isIOS;
  
  console.log("Device detection:", { isIOS, isMobile, userAgent: navigator.userAgent });
  
  const browserButton = document.getElementById('work_dir_browser');
  if (browserButton) {
    console.log("File browser button found");
    
    // Remove any existing click handlers
    browserButton.replaceWith(browserButton.cloneNode(true));
    const newButton = document.getElementById('work_dir_browser');
    
    // Enhanced click handler for iOS/mobile
    function handleFileBrowserClick(e) {
      console.log("File browser clicked - device:", { isIOS, isMobile });
      e.preventDefault();
      e.stopPropagation();
      
      if (window.fileBrowserModalProxy) {
        console.log("Opening file browser modal...");
        window.fileBrowserModalProxy.openModal();
      } else {
        console.error("fileBrowserModalProxy not available");
        if (isMobile) {
          alert("File browser loading... Please try again in a moment.");
          // Retry after a short delay on mobile
          setTimeout(() => {
            if (window.fileBrowserModalProxy) {
              window.fileBrowserModalProxy.openModal();
            }
          }, 1000);
        } else {
          alert("File browser is not available. Please check browser console for errors.");
        }
      }
    }
    
    // Add multiple event handlers for better iOS compatibility
    newButton.addEventListener('click', handleFileBrowserClick, { passive: false });
    if (isIOS) {
      newButton.addEventListener('touchstart', handleFileBrowserClick, { passive: false });
      newButton.addEventListener('touchend', function(e) {
        e.preventDefault();
      }, { passive: false });
    }
    
    // Add visual feedback
    newButton.style.cursor = 'pointer';
    newButton.style.webkitTapHighlightColor = 'rgba(0,0,0,0.1)';
    
  } else {
    console.error("File browser button not found!");
    // Try to find it with a delay (in case of dynamic loading)
    setTimeout(() => {
      const delayedButton = document.getElementById('work_dir_browser');
      if (delayedButton) {
        console.log("File browser button found after delay");
        // Recursively call this function
        document.dispatchEvent(new Event('DOMContentLoaded'));
      }
    }, 2000);
  }
});

openFileLink = async function (path) {
  try {
    const resp = await window.sendJsonData("/file_info", { path });
    if (!resp.exists) {
      window.toast("File does not exist.", "error");
      return;
    }

    if (resp.is_dir) {
      fileBrowserModalProxy.openModal(resp.abs_path);
    } else {
      fileBrowserModalProxy.downloadFile({
        path: resp.abs_path,
        name: resp.file_name,
      });
    }
  } catch (e) {
    window.toastFetchError("Error opening file", e);
  }
};
window.openFileLink = openFileLink;

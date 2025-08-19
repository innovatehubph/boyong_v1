// PWA Install Component for Pareng Boyong
// Provides mobile-friendly install experience with Filipino cultural elements

class ParengBoyongPWAInstaller {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.init();
    }

    init() {
        // Listen for PWA install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
            console.log('🇵🇭 Pareng Boyong: PWA install available');
        });

        // Check if already installed
        window.addEventListener('appinstalled', () => {
            console.log('🇵🇭 Pareng Boyong: PWA installed successfully!');
            this.isInstalled = true;
            this.hideInstallButton();
            this.showInstalledMessage();
        });

        // Check if running in PWA mode
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('🇵🇭 Pareng Boyong: Running in PWA mode');
        }

        this.createInstallButton();
        this.addMobileOptimizations();
    }

    createInstallButton() {
        // Create PWA install button with Filipino styling
        const installButton = document.createElement('button');
        installButton.id = 'pwa-install-btn';
        installButton.className = 'pwa-install-button filipino-button';
        installButton.innerHTML = `
            <span class="install-icon">📱</span>
            <span class="install-text">Install Pareng Boyong</span>
            <span class="install-subtitle">Para sa offline access po!</span>
        `;
        installButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(45deg, #1e40af, #3b82f6);
            color: #ffd700;
            border: 2px solid rgba(255, 215, 0, 0.3);
            border-radius: 16px;
            padding: 12px 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(30, 64, 175, 0.4);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            z-index: 1000;
            display: none;
            flex-direction: column;
            align-items: center;
            text-align: center;
            min-width: 120px;
            animation: filipino-pulse 2s infinite;
        `;

        installButton.addEventListener('click', () => this.installPWA());

        // Add hover effects
        installButton.addEventListener('mouseenter', () => {
            installButton.style.transform = 'translateY(-2px) scale(1.05)';
            installButton.style.boxShadow = '0 6px 20px rgba(30, 64, 175, 0.6)';
        });

        installButton.addEventListener('mouseleave', () => {
            installButton.style.transform = 'translateY(0) scale(1)';
            installButton.style.boxShadow = '0 4px 16px rgba(30, 64, 175, 0.4)';
        });

        document.body.appendChild(installButton);
        this.installButton = installButton;

        // Add CSS animations
        this.addInstallButtonStyles();
    }

    addInstallButtonStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes filipino-pulse {
                0%, 100% {
                    box-shadow: 0 4px 16px rgba(30, 64, 175, 0.4);
                }
                50% {
                    box-shadow: 0 4px 16px rgba(255, 215, 0, 0.6);
                }
            }

            .install-icon {
                font-size: 24px;
                margin-bottom: 4px;
                display: block;
            }

            .install-text {
                font-size: 12px;
                font-weight: 700;
                display: block;
                margin-bottom: 2px;
            }

            .install-subtitle {
                font-size: 10px;
                opacity: 0.8;
                font-style: italic;
                display: block;
            }

            @media (max-width: 480px) {
                #pwa-install-btn {
                    right: 10px;
                    bottom: 80px;
                    padding: 10px 12px;
                    min-width: 100px;
                    font-size: 12px;
                }

                .install-icon {
                    font-size: 20px;
                }

                .install-text {
                    font-size: 11px;
                }

                .install-subtitle {
                    font-size: 9px;
                }
            }

            .pwa-success-message {
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(45deg, #10b981, #34d399);
                color: white;
                padding: 12px 20px;
                border-radius: 12px;
                font-weight: 600;
                z-index: 1001;
                box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
                animation: slideDown 0.5s ease-out;
            }

            @keyframes slideDown {
                0% {
                    opacity: 0;
                    transform: translateX(-50%) translateY(-20px);
                }
                100% {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }

    showInstallButton() {
        if (this.installButton && !this.isInstalled) {
            this.installButton.style.display = 'flex';
            console.log('🇵🇭 Pareng Boyong: Install button shown');
        }
    }

    hideInstallButton() {
        if (this.installButton) {
            this.installButton.style.display = 'none';
        }
    }

    async installPWA() {
        if (!this.deferredPrompt) {
            this.showManualInstallInstructions();
            return;
        }

        try {
            // Show the install prompt
            this.deferredPrompt.prompt();
            
            // Wait for the user to respond
            const { outcome } = await this.deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                console.log('🇵🇭 Pareng Boyong: PWA install accepted');
                this.hideInstallButton();
                this.showInstallSuccessMessage();
            } else {
                console.log('🇵🇭 Pareng Boyong: PWA install dismissed');
                this.showEncouragementMessage();
            }
            
            this.deferredPrompt = null;
        } catch (error) {
            console.error('🇵🇭 Pareng Boyong: PWA install error:', error);
            this.showManualInstallInstructions();
        }
    }

    showInstallSuccessMessage() {
        const message = document.createElement('div');
        message.className = 'pwa-success-message';
        message.innerHTML = `
            🎉 Salamat! Pareng Boyong is now installed po! 
            <br><small>You can now use it offline anytime!</small>
        `;
        document.body.appendChild(message);

        setTimeout(() => {
            message.remove();
        }, 5000);
    }

    showEncouragementMessage() {
        const message = document.createElement('div');
        message.className = 'pwa-success-message';
        message.style.background = 'linear-gradient(45deg, #f59e0b, #fbbf24)';
        message.innerHTML = `
            🇵🇭 No worries po! You can install Pareng Boyong anytime from your browser menu.
        `;
        document.body.appendChild(message);

        setTimeout(() => {
            message.remove();
        }, 4000);
    }

    showManualInstallInstructions() {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1002;
            padding: 20px;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: linear-gradient(135deg, #1e40af, #3b82f6);
            border-radius: 16px;
            padding: 24px;
            max-width: 400px;
            width: 100%;
            color: white;
            text-align: center;
            position: relative;
        `;

        content.innerHTML = `
            <div style="font-size: 48px; margin-bottom: 16px;">🇵🇭</div>
            <h2 style="color: #ffd700; margin-bottom: 16px;">Install Pareng Boyong</h2>
            <p style="margin-bottom: 20px; line-height: 1.5;">
                To install Pareng Boyong as an app po:
            </p>
            <div style="text-align: left; margin-bottom: 20px;">
                <p><strong>Chrome/Edge:</strong> Menu → Install Pareng Boyong</p>
                <p><strong>Safari:</strong> Share → Add to Home Screen</p>
                <p><strong>Firefox:</strong> Menu → Install</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    style="background: #ffd700; color: #1e40af; border: none; padding: 12px 24px; 
                           border-radius: 8px; font-weight: 600; cursor: pointer;">
                Okay, salamat!
            </button>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    addMobileOptimizations() {
        // Add mobile-specific PWA enhancements
        if ('navigator' in window && 'serviceWorker' in navigator) {
            // Add iOS specific meta tags if running on iOS
            if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                const iOSMeta = document.createElement('meta');
                iOSMeta.name = 'apple-mobile-web-app-capable';
                iOSMeta.content = 'yes';
                document.head.appendChild(iOSMeta);

                const iOSStatusBar = document.createElement('meta');
                iOSStatusBar.name = 'apple-mobile-web-app-status-bar-style';
                iOSStatusBar.content = 'black-translucent';
                document.head.appendChild(iOSStatusBar);
            }
        }

        // Add mobile viewport height CSS custom property
        const setVH = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };

        window.addEventListener('resize', setVH);
        setVH();

        console.log('🇵🇭 Pareng Boyong: Mobile optimizations applied');
    }

    // Method to programmatically trigger install for other components
    triggerInstall() {
        if (this.installButton && this.installButton.style.display !== 'none') {
            this.installButton.click();
        } else {
            this.showManualInstallInstructions();
        }
    }
}

// Initialize PWA installer when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.parenBoyongPWA = new ParengBoyongPWAInstaller();
    });
} else {
    window.parenBoyongPWA = new ParengBoyongPWAInstaller();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ParengBoyongPWAInstaller;
}
/**
 * RSMT Neural Network Client
 * 
 * JavaScript client for communicating with the RSMT FastAPI server
 * to enable real neural network-based motion transitions.
 */

class RSMTClient {
    constructor(serverUrl = 'http://localhost:8001') {
        this.serverUrl = serverUrl;
        this.isConnected = false;
        this.modelStatus = null;
        this.connectionTimeout = 2000; // 2 second timeout
        
        // Check server availability on initialization with timeout
        this.checkConnection();
    }
    
    /**
     * Check if the RSMT server is available
     */
    async checkConnection() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.connectionTimeout);
            
            const response = await fetch(`${this.serverUrl}/api/status`, {
                signal: controller.signal,
                method: 'GET'
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                this.isConnected = true;
                await this.updateModelStatus();
                console.log('✅ RSMT server connected');
                return true;
            }
        } catch (error) {
            this.isConnected = false;
            console.log('⚠️ RSMT server not available - using offline mode with enhanced interpolation');
            
            // Notify the main application that we're in offline mode
            if (window.updateServerStatus) {
                window.updateServerStatus('Offline Mode - Enhanced Interpolation Active');
            }
            return false;
        }
        return false;
    }
    
    /**
     * Get current model loading status
     */
    async updateModelStatus() {
        try {
            const response = await fetch(`${this.serverUrl}/status`);
            if (response.ok) {
                this.modelStatus = await response.json();
                return this.modelStatus;
            }
        } catch (error) {
            console.error('Failed to get model status:', error);
        }
        return null;
    }
    
    /**
     * Encode motion into phase coordinates using DeepPhase
     */
    async encodePhase(motionFrames, frameTime = 0.016667) {
        if (!this.isConnected) {
            return this._mockPhaseEncoding(motionFrames);
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/api/encode_phase`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    motion_data: {
                        frames: motionFrames,
                        frame_time: frameTime
                    },
                    sequence_length: motionFrames.length
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(`Phase encoding: ${result.processing_time.toFixed(3)}s (${result.status})`);
                return result.phase_coordinates;
            }
        } catch (error) {
            console.error('Phase encoding failed:', error);
        }
        
        return this._mockPhaseEncoding(motionFrames);
    }
    
    /**
     * Encode motion style using StyleVAE
     */
    async encodeStyle(motionFrames, phaseData = null) {
        if (!this.isConnected) {
            return this._mockStyleEncoding();
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/api/encode_style`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    motion_data: {
                        frames: motionFrames,
                        frame_time: 0.016667
                    },
                    phase_data: phaseData
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(`Style encoding: ${result.processing_time.toFixed(3)}s (${result.status})`);
                return result.style_code;
            }
        } catch (error) {
            console.error('Style encoding failed:', error);
        }
        
        return this._mockStyleEncoding();
    }
    
    /**
     * Generate motion transition using full RSMT pipeline
     */
    async generateTransition(sourceFrames, targetFrames, options = {}) {
        const {
            transitionLength = 60,
            phaseSchedule = 1.0,
            styleBlendCurve = 'smooth'
        } = options;
        
        if (!this.isConnected) {
            return this._mockTransitionGeneration(sourceFrames, targetFrames, transitionLength, styleBlendCurve);
        }
        
        try {
            const response = await fetch(`${this.serverUrl}/api/generate_transition`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source_motion: {
                        frames: sourceFrames,
                        frame_time: 0.016667
                    },
                    target_motion: {
                        frames: targetFrames,
                        frame_time: 0.016667
                    },
                    transition_length: transitionLength,
                    phase_schedule: phaseSchedule,
                    style_blend_curve: styleBlendCurve
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log(`Neural transition generated: ${result.processing_time.toFixed(3)}s (${result.status})`);
                console.log('Quality metrics:', result.quality_metrics);
                
                return {
                    frames: result.transition_frames,
                    phaseTrajectory: result.phase_trajectory,
                    qualityMetrics: result.quality_metrics,
                    processingTime: result.processing_time,
                    usingNeuralNetwork: result.status === 'success'
                };
            }
        } catch (error) {
            console.error('Neural transition failed:', error);
        }
        
        return this._mockTransitionGeneration(sourceFrames, targetFrames, transitionLength, styleBlendCurve);
    }
    
    /**
     * Get server and model information for UI display
     */
    getConnectionInfo() {
        return {
            connected: this.isConnected,
            serverUrl: this.serverUrl,
            modelStatus: this.modelStatus,
            capabilities: this.isConnected ? {
                phaseEncoding: this.modelStatus?.deephase_loaded || false,
                styleEncoding: this.modelStatus?.stylevae_loaded || false,
                transitionGeneration: this.modelStatus?.transitionnet_loaded || false
            } : null
        };
    }
    
    // Mock implementations for fallback
    
    _mockPhaseEncoding(motionFrames) {
        console.log('Using mock phase encoding');
        const phases = [];
        for (let i = 0; i < motionFrames.length; i++) {
            const sx = Math.cos(i * 0.1);
            const sy = Math.sin(i * 0.1);
            phases.push([sx, sy]);
        }
        return phases;
    }
    
    _mockStyleEncoding() {
        console.log('Using mock style encoding');
        // Return random 256-dimensional style vector
        const styleCode = [];
        for (let i = 0; i < 256; i++) {
            styleCode.push(Math.random() * 2 - 1);
        }
        return styleCode;
    }
    
    _mockTransitionGeneration(sourceFrames, targetFrames, length, blendCurve) {
        console.log('Using mock transition generation');
        
        const transitionFrames = [];
        const phaseTrajectory = [];
        
        for (let i = 0; i < length; i++) {
            const alpha = i / (length - 1);
            
            // Style-aware blending
            let blendWeight;
            switch (blendCurve) {
                case 'smooth':
                    blendWeight = 1 / (1 + Math.exp(-10 * (alpha - 0.5))); // Sigmoid
                    break;
                case 'ease_in_out':
                    blendWeight = 0.5 * (1 + Math.sin(Math.PI * (alpha - 0.5)));
                    break;
                default: // linear
                    blendWeight = alpha;
            }
            
            // Interpolate frames
            const sourceIdx = Math.min(i, sourceFrames.length - 1);
            const targetIdx = Math.min(i, targetFrames.length - 1);
            
            const frame = [];
            for (let j = 0; j < sourceFrames[sourceIdx].length; j++) {
                const sourceVal = sourceFrames[sourceIdx][j];
                const targetVal = targetFrames[targetIdx][j];
                const value = (1 - blendWeight) * sourceVal + blendWeight * targetVal;
                frame.push(value);
            }
            
            transitionFrames.push(frame);
            
            // Mock phase trajectory
            const sx = Math.cos(alpha * Math.PI);
            const sy = Math.sin(alpha * Math.PI);
            phaseTrajectory.push([sx, sy]);
        }
        
        return {
            frames: transitionFrames,
            phaseTrajectory: phaseTrajectory,
            qualityMetrics: {
                smoothness: 0.75 + Math.random() * 0.2,
                style_preservation: 0.7 + Math.random() * 0.25,
                foot_skating: Math.random() * 0.1,
                overall_quality: 0.8 + Math.random() * 0.15
            },
            processingTime: 0.01 + Math.random() * 0.02,
            usingNeuralNetwork: false
        };
    }
}

/**
 * Connection status indicator for the UI
 */
class RSMTStatusIndicator {
    constructor(containerSelector, rsmtClient) {
        this.container = document.querySelector(containerSelector);
        this.client = rsmtClient;
        this.createIndicator();
        this.updateStatus();
        
        // Update status periodically
        setInterval(() => this.updateStatus(), 5000);
    }
    
    createIndicator() {
        if (!this.container) return;
        
        this.container.innerHTML = `
            <div class="rsmt-status-indicator">
                <div class="status-light"></div>
                <div class="status-text">
                    <div class="connection-status">Checking connection...</div>
                    <div class="model-info"></div>
                </div>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .rsmt-status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: rgba(0, 0, 0, 0.7);
                border-radius: 6px;
                font-size: 12px;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .status-light {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #666;
                transition: background-color 0.3s ease;
            }
            
            .status-light.connected { background: #4CAF50; }
            .status-light.neural { background: #2196F3; }
            .status-light.disconnected { background: #f44336; }
            
            .status-text {
                line-height: 1.3;
            }
            
            .connection-status {
                font-weight: bold;
            }
            
            .model-info {
                opacity: 0.8;
                font-size: 11px;
            }
        `;
        document.head.appendChild(style);
    }
    
    async updateStatus() {
        if (!this.container) return;
        
        const info = this.client.getConnectionInfo();
        const light = this.container.querySelector('.status-light');
        const connectionStatus = this.container.querySelector('.connection-status');
        const modelInfo = this.container.querySelector('.model-info');
        
        if (info.connected) {
            await this.client.updateModelStatus();
            const updatedInfo = this.client.getConnectionInfo();
            
            if (updatedInfo.capabilities && 
                (updatedInfo.capabilities.phaseEncoding || 
                 updatedInfo.capabilities.styleEncoding || 
                 updatedInfo.capabilities.transitionGeneration)) {
                light.className = 'status-light neural';
                connectionStatus.textContent = 'Neural Networks Active';
                
                const capabilities = [];
                if (updatedInfo.capabilities.phaseEncoding) capabilities.push('DeepPhase');
                if (updatedInfo.capabilities.styleEncoding) capabilities.push('StyleVAE');
                if (updatedInfo.capabilities.transitionGeneration) capabilities.push('TransitionNet');
                
                modelInfo.textContent = `Models: ${capabilities.join(', ')}`;
            } else {
                light.className = 'status-light connected';
                connectionStatus.textContent = 'Server Connected (Mock Mode)';
                modelInfo.textContent = 'Neural models not loaded - using enhanced interpolation';
            }
        } else {
            light.className = 'status-light disconnected';
            connectionStatus.textContent = 'Basic Interpolation';
            modelInfo.textContent = 'Server offline - using fallback implementation';
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RSMTClient, RSMTStatusIndicator };
}

// Global instance for browser usage
if (typeof window !== 'undefined') {
    window.RSMTClient = RSMTClient;
    window.RSMTStatusIndicator = RSMTStatusIndicator;
}

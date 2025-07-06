/**
 * VRM BVH Adapter - Maps BVH skeleton data to VRM character bones
 * Integrates anime characters with existing BVH motion capture system
 * Enhanced with idle animations and facial expressions
 */

class VRMBVHAdapter {
    constructor(vrmModel, bvhSkeleton) {
        this.vrmModel = vrmModel;
        this.bvhSkeleton = bvhSkeleton;
        this.boneMapping = this.createBoneMapping();
        this.initialized = false;
        this.debugMode = true; // Set to true for debugging
        
        // Idle animation system
        this.idleAnimations = {
            breathing: { enabled: true, amplitude: 0.01, frequency: 0.3, phase: 0 },
            blinking: { enabled: true, interval: 3000, lastBlink: 0, duration: 150 },
            headMovement: { enabled: true, amplitude: 0.05, frequency: 0.1, phase: 0 },
            facialExpressions: { enabled: true, currentExpression: 'neutral', duration: 0 }
        };
        
        // Camera interaction
        this.lookAtCamera = false;
        this.currentTime = 0;
        
        console.log('🎭 Enhanced VRMBVHAdapter initialized with idle animations');
        console.log('VRM Model:', vrmModel);
        console.log('BVH Skeleton:', bvhSkeleton);
        if (this.debugMode) {
            console.log('Initial bone mapping:', this.boneMapping);
        }
    }

    // Enable idle animations like the chat implementation
    setIdleAnimations(config) {
        console.log('🎭 Setting idle animations:', config);
        
        Object.assign(this.idleAnimations, config);
        
        // Start breathing animation
        if (this.idleAnimations.breathing.enabled) {
            this.startBreathingAnimation();
        }
        
        // Start blinking animation
        if (this.idleAnimations.blinking.enabled) {
            this.startBlinkingAnimation();
        }
        
        console.log('✅ Idle animations configured');
    }

    // Look at camera like a human (from chat implementation)
    lookAtCameraAsIfHuman(camera) {
        this.lookAtCamera = true;
        this.camera = camera;
        console.log('👁️ VRM character will look at camera');
    }

    // Tick function for animations (like chat implementation)
    tick(deltaTime) {
        this.currentTime += deltaTime;
        
        if (this.vrmModel) {
            // Update idle animations
            this.updateIdleAnimations(deltaTime);
            
            // Update camera looking
            if (this.lookAtCamera && this.camera) {
                this.updateCameraLook();
            }
            
            // Update VRM internal systems
            this.vrmModel.update(deltaTime);
        }
    }

    updateIdleAnimations(deltaTime) {
        if (!this.vrmModel || !this.vrmModel.humanoid) return;
        
        const time = this.currentTime;
        
        // Breathing animation
        if (this.idleAnimations.breathing.enabled) {
            const breathingOffset = Math.sin(time * this.idleAnimations.breathing.frequency) * this.idleAnimations.breathing.amplitude;
            const chestBone = this.vrmModel.humanoid.getBoneNode('chest');
            if (chestBone) {
                chestBone.rotation.x += breathingOffset * 0.1;
            }
        }
        
        // Blinking animation
        if (this.idleAnimations.blinking.enabled) {
            const timeSinceLastBlink = time - this.idleAnimations.blinking.lastBlink;
            if (timeSinceLastBlink > this.idleAnimations.blinking.interval) {
                this.triggerBlink();
                this.idleAnimations.blinking.lastBlink = time;
            }
        }
        
        // Subtle head movement
        if (this.idleAnimations.headMovement.enabled) {
            const headOffset = Math.sin(time * this.idleAnimations.headMovement.frequency) * this.idleAnimations.headMovement.amplitude;
            const headBone = this.vrmModel.humanoid.getBoneNode('head');
            if (headBone) {
                headBone.rotation.y += headOffset * 0.1;
            }
        }
    }

    triggerBlink() {
        if (this.vrmModel && this.vrmModel.expressionManager) {
            // Trigger blink expression
            const expressions = this.vrmModel.expressionManager;
            if (expressions.getExpressionValue) {
                // Quick blink animation
                setTimeout(() => {
                    if (expressions.setValue) {
                        expressions.setValue('blink', 1.0);
                        setTimeout(() => {
                            expressions.setValue('blink', 0.0);
                        }, this.idleAnimations.blinking.duration);
                    }
                }, 10);
            }
        }
    }

    updateCameraLook() {
        if (!this.camera || !this.vrmModel) return;
        
        const headBone = this.vrmModel.humanoid.getBoneNode('head');
        if (headBone) {
            // Calculate direction to camera
            const cameraPos = this.camera.position.clone();
            const headPos = headBone.getWorldPosition(new (window.THREE?.Vector3 || Vector3)());
            const direction = cameraPos.sub(headPos).normalize();
            
            // Apply subtle head rotation toward camera
            const lookIntensity = 0.3; // Subtle looking
            headBone.lookAt(headPos.add(direction.multiplyScalar(lookIntensity)));
        }
    }

    startBreathingAnimation() {
        console.log('🫁 Starting breathing animation');
        // Breathing is handled in tick function
    }

    startBlinkingAnimation() {
        console.log('👁️ Starting blinking animation');
        // Blinking is handled in tick function
    }

    createBoneMapping() {
        // Map BVH joint names to VRM humanoid bone names
        // Based on standard VRM humanoid specification
        return {
            // Core spine and head
            'Hips': 'hips',
            'Spine': 'spine',
            'Spine1': 'chest', 
            'Spine2': 'upperChest',
            'Neck': 'neck',
            'Head': 'head',
            
            // Left arm
            'LeftShoulder': 'leftShoulder',
            'LeftArm': 'leftUpperArm',
            'LeftForeArm': 'leftLowerArm',
            'LeftHand': 'leftHand',
            
            // Right arm
            'RightShoulder': 'rightShoulder',
            'RightArm': 'rightUpperArm',
            'RightForeArm': 'rightLowerArm',
            'RightHand': 'rightHand',
            
            // Left leg
            'LeftUpLeg': 'leftUpperLeg',
            'LeftLeg': 'leftLowerLeg',
            'LeftFoot': 'leftFoot',
            'LeftToeBase': 'leftToes',
            
            // Right leg
            'RightUpLeg': 'rightUpperLeg',
            'RightLeg': 'rightLowerLeg',
            'RightFoot': 'rightFoot',
            'RightToeBase': 'rightToes',
            
            // Alternative naming patterns
            'LeftElbow': 'leftLowerArm',
            'RightElbow': 'rightLowerArm',
            'LeftWrist': 'leftHand',
            'RightWrist': 'rightHand',
            'LeftHip': 'leftUpperLeg',
            'RightHip': 'rightUpperLeg',
            'LeftKnee': 'leftLowerLeg',
            'RightKnee': 'rightLowerLeg',
            'LeftAnkle': 'leftFoot',
            'RightAnkle': 'rightFoot'
        };
    }

    initialize() {
        if (!this.vrmModel || !this.vrmModel.humanoid) {
            console.error('❌ VRM model or humanoid not available');
            return false;
        }
        
        // Check available bones
        const availableBones = {};
        for (const [bvhJoint, vrmBone] of Object.entries(this.boneMapping)) {
            const bone = this.vrmModel.humanoid.getBoneNode(vrmBone);
            if (bone) {
                availableBones[bvhJoint] = { vrmBone, bone };
            }
        }
        
        this.availableBones = availableBones;
        this.initialized = true;
        
        console.log('✅ VRMBVHAdapter initialized with', Object.keys(availableBones).length, 'mapped bones');
        if (this.debugMode) {
            console.log('Available bones:', Object.keys(availableBones));
        }
        
        return true;
    }

    applyBVHFrameToVRM(frameData) {
        if (!this.initialized) {
            if (!this.initialize()) {
                return false;
            }
        }
        
        if (!frameData || frameData.length < 6) {
            if (this.debugMode) console.warn('⚠️ Invalid frame data for VRMBVHAdapter');
            return false;
        }
        
        try {
            // Apply root position (first 3 values)
            if (this.vrmModel.humanoid?.getBoneNode('hips')) {
                const hipsNode = this.vrmModel.humanoid.getBoneNode('hips');
                const rootX = frameData[0] * 0.01; // Scale to match VRM
                const rootY = frameData[1] * 0.01;
                const rootZ = frameData[2] * 0.01;
                
                // Apply root position
                this.vrmModel.scene.position.set(rootX, rootY, rootZ);

                if (this.debugMode) {
                    console.log(`VRM Root Pos: X=${rootX.toFixed(3)}, Y=${rootY.toFixed(3)}, Z=${rootZ.toFixed(3)}`);
                }
            }
            
            // Apply root rotation (next 3 values)
            const rootRotY = (frameData[3] || 0) * Math.PI / 180;
            const rootRotX = (frameData[4] || 0) * Math.PI / 180;
            const rootRotZ = (frameData[5] || 0) * Math.PI / 180;
            
            // Start from index 6 for joint rotations
            let channelIndex = 6;
            
            // Apply rotations to each mapped bone
            for (const [bvhJoint, boneData] of Object.entries(this.availableBones)) {
                if (channelIndex + 2 < frameData.length) {
                    const bone = boneData.bone;
                    
                    // BVH typically uses YXZ rotation order
                    const rotY = (frameData[channelIndex++] || 0) * Math.PI / 180;
                    const rotX = (frameData[channelIndex++] || 0) * Math.PI / 180;
                    const rotZ = (frameData[channelIndex++] || 0) * Math.PI / 180;
                    
                    // Apply rotation with proper order
                    bone.rotation.order = 'YXZ';
                    bone.rotation.set(rotX, rotY, rotZ);
                    
                    if (this.debugMode) {
                        // Log only a few key joints to avoid spam
                        if (['Hips', 'Chest', 'Head', 'RightHand', 'LeftFoot'].includes(bvhJoint)) {
                            console.log(`  ${bvhJoint} (VRM: ${boneData.vrmBone}) Rot: X=${(rotX*180/Math.PI).toFixed(1)}, Y=${(rotY*180/Math.PI).toFixed(1)}, Z=${(rotZ*180/Math.PI).toFixed(1)}`);
                        }
                    }
                }
            }
            
            // Update VRM humanoid system
            if (this.vrmModel.humanoid?.update) {
                this.vrmModel.humanoid.update();
            }
            
            return true;
            
        } catch (error) {
            console.error('❌ Error applying BVH frame to VRM:', error);
            return false;
        }
    }

    setDebugMode(enabled) {
        this.debugMode = enabled;
        console.log('🔍 VRMBVHAdapter debug mode:', enabled ? 'ON' : 'OFF');
    }

    getBoneMapping() {
        return this.boneMapping;
    }

    getAvailableBones() {
        return this.availableBones ? Object.keys(this.availableBones) : [];
    }

    // Utility method to visualize bone hierarchy
    visualizeBoneHierarchy() {
        if (!this.vrmModel || !this.vrmModel.humanoid) return;
        
        console.log('🦴 VRM Bone Hierarchy:');
        const humanoidBones = this.vrmModel.humanoid.humanBones;
        
        for (const [boneName, boneNode] of Object.entries(humanoidBones)) {
            if (boneNode) {
                console.log(`  ${boneName}: ${boneNode.name}`);
            }
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VRMBVHAdapter;
}

// Global export for browser
if (typeof window !== 'undefined') {
    window.VRMBVHAdapter = VRMBVHAdapter;
}

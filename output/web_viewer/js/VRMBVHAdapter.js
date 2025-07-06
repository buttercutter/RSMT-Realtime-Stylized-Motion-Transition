/**
 * VRM BVH Adapter - Maps BVH skeleton data to VRM character bones
 * Integrates anime characters with existing BVH motion capture system
 * Enhanced with idle animations and facial expressions
 */

class VRMBVHAdapter {
    constructor(vrmModelObject, bvhSkeleton) {
        // vrmModelObject should contain both .vrm and .scene properties
        this.vrmModelObject = vrmModelObject;
        this.vrmModel = vrmModelObject.vrm; // The actual VRM instance
        this.vrmScene = vrmModelObject.scene; // The THREE.js scene object
        this.bvhSkeleton = bvhSkeleton;
        this.boneMapping = this.createBoneMapping();
        this.availableBones = {}; // Bones that are available in the VRM model
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
        console.log('VRM Model Object:', vrmModelObject);
        console.log('VRM Instance:', this.vrmModel);
        console.log('VRM Scene:', this.vrmScene);
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
            const chestBone = this.vrmModel.humanoid.getNormalizedBoneNode('chest');
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
            const headBone = this.vrmModel.humanoid.getRawBoneNode('head');
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
        
        const headBone = this.vrmModel.humanoid.getRawBoneNode('head');
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
        // Map BVH joint names from rsmt_showcase_modern.html to VRM humanoid bone names
        // Based on standard VRM humanoid specification and the specific BVH structure
        return {
            // Root
            'Hips': 'hips',

            // Spine chain from rsmt_showcase_modern.html
            'Chest': 'spine',
            'Chest2': 'chest',
            'Chest3': 'upperChest',
            'Chest4': 'neck', // Mapping Chest4 to neck as it's the last segment before Neck in BVH
            'Neck': 'neck',
            'Head': 'head',

            // Right arm chain from rsmt_showcase_modern.html
            'RightCollar': 'rightShoulder',
            'RightShoulder': 'rightUpperArm',
            'RightElbow': 'rightLowerArm',
            'RightWrist': 'rightHand',

            // Left arm chain from rsmt_showcase_modern.html (mirrored)
            'LeftCollar': 'leftShoulder',
            'LeftShoulder': 'leftUpperArm',
            'LeftElbow': 'leftLowerArm',
            'LeftWrist': 'leftHand',

            // Right leg chain from rsmt_showcase_modern.html
            'RightHip': 'rightUpperLeg',
            'RightKnee': 'rightLowerLeg',
            'RightAnkle': 'rightFoot',
            'RightToe': 'rightToes',

            // Left leg chain from rsmt_showcase_modern.html (mirrored)
            'LeftHip': 'leftUpperLeg',
            'LeftKnee': 'leftLowerLeg',
            'LeftAnkle': 'leftFoot'
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
            // Use getNormalizedBoneNode for better compatibility and to avoid deprecation warning
            const bone = this.vrmModel.humanoid.getNormalizedBoneNode(vrmBone);
            if (bone) {
                availableBones[bvhJoint] = { vrmBone, bone };
            }
        }
        
        this.availableBones = availableBones;
        this.initialized = true;

        // Ensure autoUpdateHumanBones and lookAt.autoUpdate are true for proper VRM animation
        this.vrmModel.humanoid.autoUpdateHumanBones = true;
        if (this.vrmModel.lookAt) {
            this.vrmModel.lookAt.autoUpdate = true;
        }
        
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
        
        // Apply root position (first 3 values)
        const rootX = frameData[0] * 0.01; // Scale to match VRM
        const rootY = frameData[1] * 0.01;
        const rootZ = frameData[2] * 0.01;
        
        // Apply root position to the VRM scene directly
        this.vrmModel.scene.position.set(rootX, rootY, rootZ);

        // Apply root rotation (next 3 values)
        const rootRotY = (frameData[3] || 0) * Math.PI / 180;
        const rootRotX = (frameData[4] || 0) * Math.PI / 180;
        const rootRotZ = (frameData[5] || 0) * Math.PI / 180;
        
        // Apply root rotation to the VRM scene directly
        this.vrmModel.scene.rotation.order = 'YXZ'; // Ensure correct order
        this.vrmModel.scene.rotation.set(rootRotX, rootRotY, rootRotZ);

        if (this.debugMode) {
            console.log(`VRM Root Pos: X=${rootX.toFixed(2)}, Y=${rootY.toFixed(2)}, Z=${rootZ.toFixed(2)}`);
            console.log(`VRM Root Rot: X=${(rootRotX*180/Math.PI).toFixed(1)}, Y=${(rootRotY*180/Math.PI).toFixed(1)}, Z=${(rootRotZ*180/Math.PI).toFixed(1)}`);
        }

        // Start from index 6 for joint rotations
        let channelIndex = 6;
        
        // Apply rotations to each mapped bone
        for (const [bvhJoint, vrmBone] of Object.entries(this.boneMapping)) {
            const boneData = this.availableBones[bvhJoint];
            if (!boneData || !boneData.bone) continue; // Skip if bone not available
            
            const boneNode = boneData.bone;
            
            // Ensure bone rotation order is consistent with BVH
            boneNode.rotation.order = 'YXZ'; 

            // Check if we have enough data for this joint
            if (channelIndex + 3 > frameData.length) { // Changed to > to catch exact match for last joint
                console.warn(`⚠️ Not enough data for ${bvhJoint} (${vrmBone}). Expected 3 channels, got ${frameData.length - channelIndex}`);
                break; // Stop processing if not enough data for remaining joints
            }
            
            // Apply rotation
            const rotX = (frameData[channelIndex] || 0) * Math.PI / 180;
            const rotY = (frameData[channelIndex + 1] || 0) * Math.PI / 180;
            const rotZ = (frameData[channelIndex + 2] || 0) * Math.PI / 180;
            
            boneNode.rotation.set(rotX, rotY, rotZ);
            
            if (this.debugMode) {
                console.log(`VRM Bone ${vrmBone} (${bvhJoint}): X=${(rotX*180/Math.PI).toFixed(1)}, Y=${(rotY*180/Math.PI).toFixed(1)}, Z=${(rotZ*180/Math.PI).toFixed(1)}`);
            }
            
            channelIndex += 3; // Move to the next joint rotation
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


    // Export for use in other modules
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = VRMBVHAdapter;
    }

// Global export for browser
if (typeof window !== 'undefined') {
    window.VRMBVHAdapter = VRMBVHAdapter;
}

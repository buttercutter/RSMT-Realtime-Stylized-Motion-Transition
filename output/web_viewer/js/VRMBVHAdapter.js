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
        // Map BVH joint names to VRM humanoid bone names
        // Fixed mapping to match VRM 1.0 humanoid specification
        return {
            // Root
            'Hips': 'hips',

            // Spine chain - corrected VRM bone names
            'Chest': 'spine',
            'Chest2': 'chest', 
            'Chest3': 'upperChest',
            'Chest4': 'neck', // Chest4 maps to neck in this BVH structure
            'Neck': 'neck',   // This will be the actual neck bone
            'Head': 'head',

            // Right arm chain - corrected VRM bone names
            'RightCollar': 'rightShoulder',     // Clavicle/shoulder
            'RightShoulder': 'rightUpperArm',   // Upper arm
            'RightElbow': 'rightLowerArm',      // Forearm
            'RightWrist': 'rightHand',          // Hand

            // Left arm chain - corrected VRM bone names
            'LeftCollar': 'leftShoulder',       // Clavicle/shoulder
            'LeftShoulder': 'leftUpperArm',     // Upper arm
            'LeftElbow': 'leftLowerArm',        // Forearm
            'LeftWrist': 'leftHand',            // Hand

            // Right leg chain - corrected VRM bone names
            'RightHip': 'rightUpperLeg',        // Thigh
            'RightKnee': 'rightLowerLeg',       // Shin
            'RightAnkle': 'rightFoot',          // Foot
            'RightToe': 'rightToes',            // Toes

            // Left leg chain - corrected VRM bone names
            'LeftHip': 'leftUpperLeg',          // Thigh
            'LeftKnee': 'leftLowerLeg',         // Shin
            'LeftAnkle': 'leftFoot',            // Foot
            'LeftToe': 'leftToes'               // Toes
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

        try {
            // Apply root position (first 3 values) with proper coordinate system conversion
            const BVH_TO_METERS_SCALE = 0.01;
            const TYPICAL_HIP_HEIGHT_CM = 98.43;
            const TYPICAL_HIP_HEIGHT_METERS = TYPICAL_HIP_HEIGHT_CM * BVH_TO_METERS_SCALE;
            
            // BVH uses centimeters, VRM uses meters; BVH is Y-up, VRM is Y-up but Z-forward is flipped
            const rootX = frameData[0] * BVH_TO_METERS_SCALE;
            const rootY = (frameData[1] * BVH_TO_METERS_SCALE) - TYPICAL_HIP_HEIGHT_METERS;
            const rootZ = -frameData[2] * BVH_TO_METERS_SCALE; // Flip Z for proper VRM coordinate system
            
            this.vrmModel.scene.position.set(rootX, rootY, rootZ);

            // Apply root rotation (next 3 values) - Enhanced coordinate system conversion
            const rootRotY = (frameData[3] || 0) * Math.PI / 180; // Yaw first in BVH
            const rootRotX = (frameData[4] || 0) * Math.PI / 180; // Pitch second
            const rootRotZ = (frameData[5] || 0) * Math.PI / 180; // Roll third
            
            // Apply coordinate system corrections for VRM
            this.vrmModel.scene.rotation.order = 'YXZ'; // BVH order: Y(yaw), X(pitch), Z(roll)
            this.vrmModel.scene.rotation.set(-rootRotX, rootRotY, -rootRotZ); // Flip X and Z for VRM coordinate system

            // BVH joint order from the actual file structure (matches rsmt_showcase_modern.html)
            const bvhJointOrder = [
                'Hips', 'Chest', 'Chest2', 'Chest3', 'Chest4', 'Neck', 'Head',
                'RightCollar', 'RightShoulder', 'RightElbow', 'RightWrist',
                'LeftCollar', 'LeftShoulder', 'LeftElbow', 'LeftWrist',
                'RightHip', 'RightKnee', 'RightAnkle', 'RightToe',
                'LeftHip', 'LeftKnee', 'LeftAnkle', 'LeftToe'
            ];

            // Start from index 6 for joint rotations (after root pos + rot)
            let channelIndex = 6;
            
            // Process joints in BVH file order, not bone mapping order
            for (const bvhJoint of bvhJointOrder) {
                // Skip root joint as it's already processed
                if (bvhJoint === 'Hips') continue;
                
                // Check if this BVH joint maps to a VRM bone
                const vrmBoneName = this.boneMapping[bvhJoint];
                if (!vrmBoneName) {
                    // Skip unmapped joints but advance channel index
                    channelIndex += 3;
                    continue;
                }
                
                const boneData = this.availableBones[bvhJoint];
                if (!boneData || !boneData.bone) {
                    // Skip unavailable bones but advance channel index
                    channelIndex += 3;
                    continue;
                }
                
                const boneNode = boneData.bone;
                
                // Check if we have enough data for this joint
                if (channelIndex + 2 >= frameData.length) {
                    console.warn(`⚠️ Not enough data for ${bvhJoint} (${vrmBoneName}). Frame data length: ${frameData.length}, needed index: ${channelIndex + 2}`);
                    break;
                }
                
                // BVH rotation order is typically Y, X, Z (yaw, pitch, roll)
                const rotY = (frameData[channelIndex] || 0) * Math.PI / 180;     // Yaw
                const rotX = (frameData[channelIndex + 1] || 0) * Math.PI / 180; // Pitch  
                const rotZ = (frameData[channelIndex + 2] || 0) * Math.PI / 180; // Roll
                
                // Apply coordinate system conversion for VRM
                // VRM uses different coordinate conventions than BVH
                boneNode.rotation.order = 'YXZ'; // Match BVH rotation order
                
                // Apply rotations with coordinate system corrections
                if (bvhJoint.includes('Right')) {
                    // Right side bones might need different coordinate mapping
                    boneNode.rotation.set(-rotX, rotY, -rotZ); // Flip X and Z for right side
                } else if (bvhJoint.includes('Left')) {
                    // Left side bones
                    boneNode.rotation.set(-rotX, -rotY, rotZ); // Different mapping for left side
                } else {
                    // Central bones (spine, neck, head)
                    boneNode.rotation.set(-rotX, rotY, rotZ); // Standard conversion
                }
                
                if (this.debugMode && channelIndex < 15) { // Only log first few bones to avoid spam
                    console.log(`${bvhJoint} -> ${vrmBoneName}: Y=${(rotY*180/Math.PI).toFixed(1)}, X=${(rotX*180/Math.PI).toFixed(1)}, Z=${(rotZ*180/Math.PI).toFixed(1)}`);
                }
                
                channelIndex += 3;
            }
            
            // Update VRM using the correct method - this is critical!
            // VRM models need to be updated with deltaTime, not just humanoid.update()
            if (this.vrmModel && this.vrmModel.update) {
                // Use a fixed deltaTime if not provided - this is essential for VRM animation
                const deltaTime = 1/60; // 60fps
                this.vrmModel.update(deltaTime);
            } else if (this.vrmModel.humanoid?.update) {
                // Fallback for older VRM versions
                this.vrmModel.humanoid.update();
            }
            
            return true;
            
        } catch (error) {
            console.error('❌ Error applying BVH frame to VRM:', error);
            return false;
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

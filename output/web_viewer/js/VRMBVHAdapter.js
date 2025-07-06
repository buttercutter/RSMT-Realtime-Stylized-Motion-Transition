/**
 * VRM BVH Adapter - Maps BVH skeleton data to VRM character bones
 * Integrates anime characters with existing BVH motion capture system
 */

class VRMBVHAdapter {
    constructor(vrmModel, bvhSkeleton) {
        this.vrmModel = vrmModel;
        this.bvhSkeleton = bvhSkeleton;
        this.boneMapping = this.createBoneMapping();
        this.initialized = false;
        this.debugMode = true; // Set to true for debugging
        
        console.log('🎭 VRMBVHAdapter initialized');
        console.log('VRM Model:', vrmModel);
        console.log('BVH Skeleton:', bvhSkeleton);
        if (this.debugMode) {
            console.log('Initial bone mapping:', this.boneMapping);
        }
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

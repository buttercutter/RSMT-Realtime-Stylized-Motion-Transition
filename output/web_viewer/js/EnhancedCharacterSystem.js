/**
 * Enhanced Character System - Integrates VRM characters with BVH skeleton system
 * Provides classroom environment and character management for RSMT
 */

class EnhancedCharacterSystem {
    constructor(scene, bvhSkeleton) {
        this.scene = scene;
        this.bvhSkeleton = bvhSkeleton;
        this.vrmModel = null;
        this.vrmAdapter = null;
        this.classroomEnvironment = null;
        this.materialExtractor = null;
        this.displayMode = 'textured_skeleton'; // 'skeleton', 'character', 'both', 'textured_skeleton'
        this.currentCharacter = null;
        this.facialExpressionSystem = null;
        this.animationBlender = null;
        this.initialized = false;
        this.debugMode = true; // Enable debug mode for EnhancedCharacterSystem
        
        // Wait for THREE to be available
        this.THREE = window.THREE || null;
        if (!this.THREE) {
            console.warn('⚠️ THREE.js not yet available, will retry...');
        }
        
        console.log('🎭 EnhancedCharacterSystem initialized');
    }

    async loadVRMCharacter(characterPath) {
        try {
            console.log('🎭 Loading VRM character:', characterPath);
            if (this.debugMode) console.log('  Character path:', characterPath);
            
            // Ensure THREE is available
            if (!this.THREE) {
                this.THREE = window.THREE;
                if (!this.THREE) {
                    throw new Error('THREE.js not available');
                }
            }
            
            // Dynamic import of VRM loader
            const { GLTFLoader } = await import('https://cdn.jsdelivr.net/npm/three@0.177.0/examples/jsm/loaders/GLTFLoader.js');
            const { VRMLoaderPlugin } = await import('https://cdn.jsdelivr.net/npm/@pixiv/three-vrm@2.0.6/lib/three-vrm.module.js');
            
            const loader = new GLTFLoader();
            loader.register((parser) => new VRMLoaderPlugin(parser));
            
            // Load VRM model
            const gltf = await new Promise((resolve, reject) => {
                loader.load(
                    characterPath,
                    (gltf) => {
                        console.log('✅ VRM file loaded successfully');
                        if (this.debugMode) console.log('  GLTF object:', gltf);
                        resolve(gltf);
                    },
                    (progress) => {
                        if (this.debugMode) console.log('📈 Loading progress:', (progress.loaded / progress.total * 100).toFixed(1) + '%');
                    },
                    (error) => {
                        console.error('❌ Failed to load VRM file:', error);
                        reject(error);
                    }
                );
            });
            
            this.vrmModel = gltf.userData.vrm;
            this.currentCharacter = characterPath;
            
            // Initialize VRM adapter
            this.vrmAdapter = new VRMBVHAdapter(this.vrmModel, this.bvhSkeleton);
            if (this.debugMode) console.log('  VRMBVHAdapter initialized:', this.vrmAdapter);
            
            // Set up idle animations like in the chat implementation
            this.vrmAdapter.setIdleAnimations({
                breathing: { enabled: true, amplitude: 0.015, frequency: 0.3 },
                blinking: { enabled: true, interval: 2500, duration: 120 },
                headMovement: { enabled: true, amplitude: 0.03, frequency: 0.08 },
                facialExpressions: { enabled: true, currentExpression: 'neutral' }
            });
            
            // Enable camera looking behavior
            if (this.scene.getObjectByName && this.scene.getObjectByName('camera')) {
                this.vrmAdapter.lookAtCameraAsIfHuman(this.scene.getObjectByName('camera'));
            }
            
            // Scale and position VRM to match BVH skeleton
            this.vrmModel.scene.scale.setScalar(0.01); // Adjust scale as needed
            this.vrmModel.scene.position.set(0, 0, 0);
            this.vrmModel.scene.rotation.set(0, 0, 0);
            
            // Set initial visibility based on display mode
            this.vrmModel.scene.visible = (this.displayMode === 'character' || this.displayMode === 'both');
            
            // Add to scene
            this.scene.add(this.vrmModel.scene);
            
            // Initialize facial expression system
            this.facialExpressionSystem = new FacialExpressionSystem(this.vrmModel);
            
            // Initialize animation blender
            this.animationBlender = new AnimationBlender(this);
            
            // Enable shadows
            this.vrmModel.scene.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
            
            console.log('✅ VRM character loaded and rigged to BVH skeleton');
            console.log('Character:', this.currentCharacter);
            
            return this.vrmModel;
            
        } catch (error) {
            console.error('❌ Failed to load VRM character:', error);
            throw error;
        }
    }

    async loadClassroomEnvironment() {
        try {
            console.log('🏫 Loading classroom environment from GLB...');
            
            // Dynamic import of GLTFLoader
            const { GLTFLoader } = await import('https://cdn.jsdelivr.net/npm/three@0.177.0/examples/jsm/loaders/GLTFLoader.js');
            const loader = new GLTFLoader();
            
            // Load GLB model
            const gltf = await new Promise((resolve, reject) => {
                loader.load(
                    './assets/scenes/classroom.glb', // Path to the classroom GLB
                    (gltf) => {
                        console.log('✅ Classroom GLB loaded successfully');
                        if (this.debugMode) console.log('  Classroom GLTF object:', gltf);
                        resolve(gltf);
                    },
                    (progress) => {
                        if (this.debugMode) console.log('📈 Classroom loading progress:', (progress.loaded / progress.total * 100).toFixed(1) + '%');
                    },
                    (error) => {
                        console.error('❌ Failed to load classroom GLB:', error);
                        if (this.debugMode) console.error('  Classroom GLB loading error details:', error);
                        reject(error);
                    }
                );
            });
            
            this.classroomEnvironment = gltf.scene;
            
            // Scale and position the classroom if necessary
            this.classroomEnvironment.scale.setScalar(1); // Adjust scale as needed
            this.classroomEnvironment.position.set(0, 0, 0);
            
            // Enable shadows for all meshes in the classroom
            this.classroomEnvironment.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
            
            // Add to scene
            this.scene.add(this.classroomEnvironment);
            
            console.log('✅ Classroom environment loaded from GLB');
            
        } catch (error) {
            console.error('❌ Failed to load classroom environment from GLB:', error);
            throw error;
        }
    }

    setDisplayMode(mode) {
        this.displayMode = mode;
        
        // Control visibility of skeleton vs character
        if (this.bvhSkeleton) {
            this.bvhSkeleton.visible = (mode === 'skeleton' || mode === 'both');
        }
        
        if (this.vrmModel) {
            this.vrmModel.scene.visible = (mode === 'character' || mode === 'both');
        }
        
        console.log('🎭 Display mode changed to:', mode);
    }

    toggleClassroomVisibility() {
        if (this.classroomEnvironment) {
            this.classroomEnvironment.visible = !this.classroomEnvironment.visible;
            console.log('🏫 Classroom visibility:', this.classroomEnvironment.visible ? 'ON' : 'OFF');
            return this.classroomEnvironment.visible;
        }
        return false;
    }

    applyBVHFrame(frameData) {
        // Apply BVH data to VRM character
        if (this.vrmAdapter && this.vrmModel && frameData) {
            if (this.debugMode && Math.random() < 0.01) { // Log occasionally to avoid spam
                console.log('  ECS: Applying BVH frame to VRM. Frame data length:', frameData.length);
                console.log('  ECS: First 6 values of frameData (root pos/rot):', frameData.slice(0, 6).map(v => v.toFixed(2)));
            }
            this.vrmAdapter.applyBVHFrameToVRM(frameData);
            
            // Update facial expressions based on motion
            if (this.facialExpressionSystem) {
                this.facialExpressionSystem.updateFromMotion(frameData);
            }
        }
    }

    resetCharacterPosition() {
        if (this.vrmModel) {
            this.vrmModel.scene.position.set(0, 0, 0);
            this.vrmModel.scene.rotation.set(0, 0, 0);
            this.vrmModel.scene.scale.setScalar(0.01);
            console.log('↺ Character position reset');
        }
    }

    update() {
        // Update VRM systems
        if (this.vrmModel?.update) {
            this.vrmModel.update();
        }
        
        // Update facial expressions
        if (this.facialExpressionSystem) {
            this.facialExpressionSystem.update();
        }
        
        // Update animation blender
        if (this.animationBlender) {
            this.animationBlender.update();
        }
    }

    getCharacterList() {
        return [
            { name: 'Kaede', file: 'kaede.vrm', description: 'School Girl' },
            { name: 'Ichika', file: 'ichika.vrm', description: 'Student' },
            { name: 'Buny', file: 'buny.vrm', description: 'Teacher' }
        ];
    }

    getCurrentCharacter() {
        return this.currentCharacter;
    }

    // Apply VRM textures to BVH skeleton instead of loading separate VRM
    async applyVRMTextureToSkeleton(vrmPath) {
        try {
            console.log('🎨 Applying VRM textures to skeleton:', vrmPath);
            
            // Initialize material extractor if not done
            if (!this.materialExtractor) {
                // Use globally available VRMMaterialExtractor
                if (window.VRMMaterialExtractor) {
                    this.materialExtractor = new window.VRMMaterialExtractor();
                } else {
                    throw new Error('VRMMaterialExtractor not available');
                }
            }
            
            // Load VRM and extract materials
            await this.materialExtractor.loadVRM(vrmPath);
            
            // Apply materials to the BVH skeleton
            if (this.materialExtractor) {
                try {
                    this.materialExtractor.applyMaterialsToSkeleton(this.bvhSkeleton);
                    
                    // Apply clothing as separate meshes if available
                    this.materialExtractor.applyClothingMeshes(this.scene);
                    
                    this.displayMode = 'textured_skeleton';
                    console.log('✨ VRM textures applied to skeleton successfully');
                } catch (applyError) {
                    console.error('Error applying materials to skeleton:', applyError);
                    console.log('Falling back to basic skeleton display');
                    this.displayMode = 'skeleton';
                }
            } else {
                console.warn('Material extractor not available, using basic skeleton display');
                this.displayMode = 'skeleton';
            }
            
            return true;
        } catch (error) {
            console.error('❌ Failed to apply VRM textures:', error);
            return false;
        }
    }

    // Load classroom environment
    async loadClassroomEnvironment() {
        try {
            console.log('🏫 Loading classroom environment...');
            
            // Use globally available ClassroomEnvironment
            if (window.ClassroomEnvironment) {
                this.classroomEnvironment = new window.ClassroomEnvironment(this.scene);
            } else {
                throw new Error('ClassroomEnvironment not available');
            }
            
            // Load the classroom
            await this.classroomEnvironment.loadClassroom({
                deskCount: 15,
                rows: 3
            });
            
            // Set optimal camera position for classroom view
            const cameraPos = this.classroomEnvironment.getOptimalCameraPosition();
            if (this.scene.userData.controls) {
                this.scene.userData.controls.object.position.copy(cameraPos.position);
                this.scene.userData.controls.target.copy(cameraPos.target);
                this.scene.userData.controls.update();
            }
            
            console.log('✅ Classroom environment loaded');
            return true;
        } catch (error) {
            console.error('❌ Failed to load classroom:', error);
            return false;
        }
    }

    // Initialize complete textured skeleton in classroom
    async initializeTexturedSkeletonInClassroom(characterName = 'ichika') {
        try {
            console.log('🚀 Initializing textured skeleton in classroom...');
            
            // Load classroom environment
            await this.loadClassroomEnvironment();
            
            // Apply VRM textures to skeleton
            const vrmPath = `/assets/avatars/${characterName}.vrm`;
            await this.applyVRMTextureToSkeleton(vrmPath);
            
            // Position skeleton in classroom
            this.positionSkeletonInClassroom();
            
            this.initialized = true;
            console.log('🎉 Textured skeleton in classroom ready!');
            
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize textured skeleton in classroom:', error);
            return false;
        }
    }

    positionSkeletonInClassroom() {
        if (!this.bvhSkeleton) {
            console.warn('No BVH skeleton available for positioning');
            return;
        }
        
        // Check different possible skeleton structures for bones
        let bones = null;
        if (this.bvhSkeleton.bones && Array.isArray(this.bvhSkeleton.bones)) {
            bones = this.bvhSkeleton.bones;
        } else if (this.bvhSkeleton.children && Array.isArray(this.bvhSkeleton.children)) {
            bones = this.bvhSkeleton.children;
        } else {
            // Try to find bones by traversing
            const foundBones = [];
            this.bvhSkeleton.traverse((child) => {
                if (child.isBone || child.type === 'Bone' || child.name.includes('bone') || child.name.includes('Bone')) {
                    foundBones.push(child);
                }
            });
            bones = foundBones;
        }
        
        if (!bones || bones.length === 0) {
            console.warn('No bones found in skeleton for positioning');
            console.log('Skeleton structure:', this.bvhSkeleton);
            return;
        }
        
        // Position the skeleton in the center of the classroom walking area
        const hipsBone = bones.find(bone => bone.name === 'Hips' || bone.name === 'hips' || bone.name.toLowerCase().includes('hip'));
        if (hipsBone) {
            hipsBone.position.set(0, 0, 0); // Center of classroom
            console.log('📍 Skeleton positioned in classroom');
        } else {
            // If no hips bone found, position the whole skeleton
            this.bvhSkeleton.position.set(0, 0, 0);
            console.log('📍 Skeleton positioned in classroom (whole skeleton)');
        }
    }

    // Get walking area boundaries for animation
    getClassroomWalkingArea() {
        if (this.classroomEnvironment) {
            return this.classroomEnvironment.getWalkingArea();
        }
        return {
            minX: -8,
            maxX: 8,
            minZ: -6,
            maxZ: 4,
            floorY: 0
        };
    }

    // Switch between display modes
    setDisplayMode(mode) {
        this.displayMode = mode;
        console.log(`🔄 Display mode changed to: ${mode}`);
        
        // Handle visibility based on mode
        if (this.bvhSkeleton) {
            this.bvhSkeleton.visible = (mode === 'skeleton' || mode === 'both' || mode === 'textured_skeleton');
        }
        
        if (this.vrmModel) {
            this.vrmModel.scene.visible = (mode === 'character' || mode === 'both');
        }
    }

    dispose() {
        if (this.vrmModel) {
            this.scene.remove(this.vrmModel.scene);
            this.vrmModel = null;
        }
        
        if (this.classroomEnvironment) {
            this.classroomEnvironment.dispose();
            this.classroomEnvironment = null;
        }
        
        if (this.materialExtractor) {
            this.materialExtractor.dispose();
            this.materialExtractor = null;
        }
        
        this.vrmAdapter = null;
        this.facialExpressionSystem = null;
        this.animationBlender = null;
        
        console.log('🗑️ Character system disposed');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedCharacterSystem;
}

// Global export for browser
if (typeof window !== 'undefined') {
    window.EnhancedCharacterSystem = EnhancedCharacterSystem;
}

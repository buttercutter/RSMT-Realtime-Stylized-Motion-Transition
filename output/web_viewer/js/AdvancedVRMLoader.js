/**
 * Advanced VRM Character Loader
 * Based on the chat folder implementation for proper VRM character animation
 */

class AdvancedVRMLoader {
    constructor() {
        this.loadedVRMs = new Map();
        this.currentVRM = null;
    }

    async loadVRMCharacter(vrmPath, scene) {
        try {
            console.log('🎭 Loading VRM character with proper animation:', vrmPath);
            
            // Check cache first
            if (this.loadedVRMs.has(vrmPath)) {
                console.log('📦 Using cached VRM:', vrmPath);
                return this.cloneVRM(this.loadedVRMs.get(vrmPath), scene);
            }

            // Use the global VRM loader that's already set up
            if (!window.THREELoaders?.GLTFLoader || !window.THREELoaders?.VRMLoaderPlugin) {
                throw new Error('VRM loaders not available');
            }

            const loader = new window.THREELoaders.GLTFLoader();
            loader.register((parser) => new window.THREELoaders.VRMLoaderPlugin(parser));

            // Load VRM with proper progress tracking
            const gltf = await new Promise((resolve, reject) => {
                loader.load(
                    vrmPath,
                    (gltf) => {
                        console.log('✅ VRM file loaded successfully');
                        resolve(gltf);
                    },
                    (progress) => {
                        const percent = (progress.loaded / progress.total * 100).toFixed(1);
                        if (Math.random() < 0.1) { // Log occasionally to avoid spam
                            console.log('📈 VRM loading progress:', percent + '%');
                        }
                    },
                    (error) => {
                        console.error('❌ Failed to load VRM file:', error);
                        reject(error);
                    }
                );
            });

            // Process VRM
            const vrm = gltf.userData.vrm;
            if (!vrm) {
                throw new Error('No VRM data found in file');
            }

            // Wait for VRM to be ready
            await vrm.ready;

            // Configure VRM for better rendering
            this.configureVRMForRendering(vrm);

            // Set up idle animations like in chat implementation
            this.setupIdleAnimations(vrm);

            // Cache the VRM
            this.loadedVRMs.set(vrmPath, { gltf, vrm });

            // Add to scene and return
            const vrmInstance = this.createVRMInstance(gltf, vrm, scene);
            this.currentVRM = vrmInstance;

            console.log('🎉 VRM character loaded and configured!');
            return vrmInstance;

        } catch (error) {
            console.error('❌ Failed to load VRM character:', error);
            throw error;
        }
    }

    configureVRMForRendering(vrm) {
        console.log('⚙️ Configuring VRM for optimal rendering...');

        // Configure materials for better lighting (no shadows for compatibility)
        if (vrm.scene) {
            vrm.scene.traverse((child) => {
                if (child.isMesh && child.material) {
                    // Completely disable shadows for VRM materials to prevent shader errors
                    child.castShadow = false;
                    child.receiveShadow = false;

                    // Configure material for better lighting without shadows
                    try {
                        if (child.material.isMeshStandardMaterial || child.material.isMeshPhysicalMaterial) {
                            child.material.envMapIntensity = 0.8;
                            child.material.roughness = 0.8;
                            child.material.metalness = 0.1;
                        }

                        // Make materials more responsive to lighting
                        if (child.material.emissive) {
                            child.material.emissive.multiplyScalar(0.1);
                        }
                        
                        // Force material update to apply changes
                        child.material.needsUpdate = true;
                        
                    } catch (materialError) {
                        console.warn('⚠️ Could not configure material for:', child.name, materialError.message);
                    }
                }
            });
        }

        // Configure humanoid if available
        if (vrm.humanoid) {
            console.log('🤖 Configuring VRM humanoid bones...');
            // Set up bone constraints and limits
        }

        console.log('✅ VRM rendering configuration complete (no shadows for compatibility)');
    }

    setupIdleAnimations(vrm) {
        console.log('😊 Setting up VRM idle animations...');

        // Set up facial expressions
        if (vrm.expressionManager) {
            vrm.expressionManager.setValue('neutral', 1.0);
            
            // Set up blinking animation
            this.setupBlinking(vrm);
        }

        // Set up breathing animation
        if (vrm.humanoid) {
            this.setupBreathing(vrm);
        }

        console.log('✅ Idle animations configured');
    }

    setupBlinking(vrm) {
        if (!vrm.expressionManager) return;

        const blinkInterval = 2000 + Math.random() * 2000; // 2-4 seconds
        
        setTimeout(() => {
            this.triggerBlink(vrm);
            this.setupBlinking(vrm); // Schedule next blink
        }, blinkInterval);
    }

    triggerBlink(vrm) {
        if (!vrm.expressionManager) return;

        // Quick blink animation
        vrm.expressionManager.setValue('blink', 1.0);
        setTimeout(() => {
            vrm.expressionManager.setValue('blink', 0.0);
        }, 150);
    }

    setupBreathing(vrm) {
        if (!vrm.humanoid) return;

        // Subtle breathing animation
        const chestBone = vrm.humanoid.getBoneNode('chest');
        if (chestBone) {
            const originalRotation = chestBone.rotation.clone();
            
            const breathe = (time) => {
                const breathingCycle = Math.sin(time * 0.0008) * 0.02; // Very subtle
                chestBone.rotation.x = originalRotation.x + breathingCycle;
                
                requestAnimationFrame(breathe);
            };
            
            requestAnimationFrame(breathe);
        }
    }

    createVRMInstance(gltf, vrm, scene) {
        console.log('🎭 Creating VRM instance...');

        // Scale appropriately for the scene
        const scale = 1.0; // Use full scale for VRM
        gltf.scene.scale.setScalar(scale);

        // Position in scene
        gltf.scene.position.set(0, 0, 0);
        gltf.scene.rotation.set(0, 0, 0);

        // Add to scene
        scene.add(gltf.scene);

        // Create instance object
        const instance = {
            scene: gltf.scene,
            vrm: vrm,
            gltf: gltf,
            
            // Utility methods
            setPosition: (x, y, z) => {
                gltf.scene.position.set(x, y, z);
            },
            
            setRotation: (x, y, z) => {
                gltf.scene.rotation.set(x, y, z);
            },
            
            setScale: (scale) => {
                gltf.scene.scale.setScalar(scale);
            },
            
            lookAtCamera: (camera) => {
                this.setupCameraLooking(vrm, camera);
            },
            
            update: (deltaTime) => {
                if (vrm) {
                    vrm.update(deltaTime);
                }
            },
            
            dispose: () => {
                scene.remove(gltf.scene);
            }
        };

        console.log('✅ VRM instance created');
        return instance;
    }

    setupCameraLooking(vrm, camera) {
        if (!vrm.humanoid) return;

        const headBone = vrm.humanoid.getBoneNode('head');
        if (!headBone) return;

        // Set up camera looking behavior
        const lookAtCamera = () => {
            if (!camera) return;

            const headPosition = new window.THREE.Vector3();
            headBone.getWorldPosition(headPosition);

            const cameraPosition = camera.position.clone();
            const direction = cameraPosition.sub(headPosition).normalize();

            // Apply subtle head rotation toward camera
            const lookIntensity = 0.2; // Subtle looking
            const targetRotation = new window.THREE.Euler().setFromVector3(direction.multiplyScalar(lookIntensity));
            
            // Lerp toward target rotation for smooth movement
            headBone.rotation.x = window.THREE.MathUtils.lerp(headBone.rotation.x, targetRotation.x, 0.02);
            headBone.rotation.y = window.THREE.MathUtils.lerp(headBone.rotation.y, targetRotation.y, 0.02);
        };

        // Update in animation loop
        const animate = () => {
            lookAtCamera();
            requestAnimationFrame(animate);
        };
        animate();
    }

    cloneVRM(cachedVRM, scene) {
        console.log('📦 Cloning cached VRM...');
        
        // For now, return a new instance from cache
        // In a more sophisticated implementation, we'd properly clone the VRM
        return this.createVRMInstance(cachedVRM.gltf, cachedVRM.vrm, scene);
    }

    dispose() {
        this.loadedVRMs.clear();
        this.currentVRM = null;
    }
}

// Global export
if (typeof window !== 'undefined') {
    window.AdvancedVRMLoader = AdvancedVRMLoader;
}

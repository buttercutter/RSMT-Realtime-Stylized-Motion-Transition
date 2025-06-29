#!/usr/bin/env python3
"""
RSMT Results Visualizer

This script creates multiple visualization options for viewing RSMT results:
1. Generate sample animations
2. Create a simple 3D matplotlib viewer
3. Set up web-based viewer
4. Prepare files for Blender import
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pickle

# Add project to path
sys.path.append('.')

def generate_demo_animations():
    """Generate several demo animations to visualize"""
    print("🎬 Generating Demo Animations...")
    
    # Create output directory
    os.makedirs("output/demo_visualizations", exist_ok=True)
    
    # Generate different types of animations
    animations_to_create = [
        ("basic_pipeline", "python test_pipeline.py"),
        ("complete_system", "python final_test.py"),
        ("bvh_writer_test", "python test_bvh_writer.py")
    ]
    
    for name, command in animations_to_create:
        print(f"  Creating {name}...")
        os.system(command)
    
    # List all generated BVH files
    bvh_files = []
    for root, dirs, files in os.walk("output"):
        for file in files:
            if file.endswith(".bvh"):
                bvh_files.append(os.path.join(root, file))
    
    print(f"✅ Generated {len(bvh_files)} BVH animation files:")
    for bvh in bvh_files:
        print(f"   📁 {bvh}")
    
    return bvh_files

def create_simple_3d_viewer():
    """Create a simple matplotlib-based 3D skeleton viewer"""
    print("\n🎯 Creating Simple 3D Viewer...")
    
    try:
        # Create synthetic skeleton data for visualization
        num_joints = 22
        parents = [-1, 0, 1, 2, 3, 0, 5, 6, 7, 0, 9, 10, 11, 12, 13, 12, 15, 16, 17, 12, 19, 20, 21][:num_joints]
        joint_names = ["Hips", "LeftHip", "LeftKnee", "LeftAnkle", "LeftToe",
                      "RightHip", "RightKnee", "RightAnkle", "RightToe",
                      "Chest", "Chest2", "Chest3", "Chest4", "Neck", "Head",
                      "LeftCollar", "LeftShoulder", "LeftElbow", "LeftWrist",
                      "RightCollar", "RightShoulder", "RightElbow"][:num_joints]
        
        # Create basic T-pose offsets
        offsets = np.zeros((num_joints, 3))
        offsets[1] = [-0.2, -0.1, 0]   # LeftHip
        offsets[2] = [0, -0.5, 0]      # LeftKnee
        offsets[3] = [0, -0.5, 0]      # LeftAnkle
        offsets[4] = [0, -0.1, 0.2]    # LeftToe
        offsets[5] = [0.2, -0.1, 0]    # RightHip
        offsets[6] = [0, -0.5, 0]      # RightKnee
        offsets[7] = [0, -0.5, 0]      # RightAnkle
        offsets[8] = [0, -0.1, 0.2]    # RightToe
        offsets[9] = [0, 0.2, 0]       # Chest
        offsets[13] = [0, 0.1, 0]      # Neck
        offsets[14] = [0, 0.1, 0]      # Head
        offsets[15] = [-0.2, 0, 0]     # LeftCollar
        offsets[16] = [-0.3, 0, 0]     # LeftShoulder
        offsets[17] = [0, -0.3, 0]     # LeftElbow
        offsets[18] = [0, -0.3, 0]     # LeftWrist
        offsets[19] = [0.2, 0, 0]      # RightCollar
        offsets[20] = [0.3, 0, 0]      # RightShoulder
        offsets[21] = [0, -0.3, 0]     # RightElbow
        
        # Generate animated motion
        num_frames = 60
        positions = np.zeros((num_frames, num_joints, 3))
        
        for frame in range(num_frames):
            # Calculate joint positions with simple animation
            positions[frame] = calculate_skeleton_positions(offsets, parents, frame, num_frames)
        
        # Create animated plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        def animate_frame(frame_idx):
            ax.clear()
            
            pos = positions[frame_idx]
            
            # Plot joints
            ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], 
                      c='red', s=50, alpha=0.8)
            
            # Plot bones
            for i in range(1, num_joints):
                if parents[i] >= 0:
                    parent_pos = pos[parents[i]]
                    joint_pos = pos[i]
                    ax.plot([parent_pos[0], joint_pos[0]],
                           [parent_pos[1], joint_pos[1]], 
                           [parent_pos[2], joint_pos[2]], 
                           'b-', linewidth=2, alpha=0.7)
            
            # Add joint labels for key joints
            key_joints = [0, 9, 14, 16, 18, 20, 21]  # Hips, Chest, Head, Shoulders, Wrists
            for i in key_joints:
                if i < len(joint_names):
                    ax.text(pos[i, 0], pos[i, 1], pos[i, 2], 
                           joint_names[i], fontsize=8)
            
            # Set axis properties
            ax.set_xlim([-1, 1])
            ax.set_ylim([-2, 1])
            ax.set_zlim([0, 2])
            ax.set_xlabel('X (left-right)')
            ax.set_ylabel('Y (forward-back)')
            ax.set_zlabel('Z (up-down)')
            ax.set_title(f'RSMT Skeleton Animation - Frame {frame_idx + 1}/{num_frames}')
            
            # Set a good viewing angle
            ax.view_init(elev=15, azim=45 + frame_idx * 2)  # Slowly rotate view
        
        print("  📊 Creating animated plot...")
        
        # Show a few key frames as static plots
        key_frames = [0, num_frames//4, num_frames//2, 3*num_frames//4]
        fig_static, axes = plt.subplots(2, 2, figsize=(15, 12), subplot_kw={'projection': '3d'})
        axes = axes.flatten()
        
        for i, frame_idx in enumerate(key_frames):
            ax = axes[i]
            pos = positions[frame_idx]
            
            # Plot joints
            ax.scatter(pos[:, 0], pos[:, 1], pos[:, 2], 
                      c='red', s=30, alpha=0.8)
            
            # Plot bones
            for j in range(1, num_joints):
                if parents[j] >= 0:
                    parent_pos = pos[parents[j]]
                    joint_pos = pos[j]
                    ax.plot([parent_pos[0], joint_pos[0]],
                           [parent_pos[1], joint_pos[1]], 
                           [parent_pos[2], joint_pos[2]], 
                           'b-', linewidth=1.5, alpha=0.7)
            
            ax.set_xlim([-1, 1])
            ax.set_ylim([-2, 1])
            ax.set_zlim([0, 2])
            ax.set_title(f'Frame {frame_idx + 1}')
            ax.view_init(elev=15, azim=45)
        
        plt.tight_layout()
        plt.savefig('output/demo_visualizations/skeleton_keyframes.png', dpi=150, bbox_inches='tight')
        print("  ✅ Saved static visualization: output/demo_visualizations/skeleton_keyframes.png")
        
        # Create an animated GIF if pillow is available
        try:
            from matplotlib.animation import FuncAnimation
            print("  🎬 Creating animated GIF...")
            
            fig_anim = plt.figure(figsize=(10, 8))
            ax_anim = fig_anim.add_subplot(111, projection='3d')
            
            anim = FuncAnimation(fig_anim, lambda frame: animate_frame(frame), 
                               frames=num_frames, interval=100, repeat=True)
            
            anim.save('output/demo_visualizations/skeleton_animation.gif', 
                     writer='pillow', fps=10)
            print("  ✅ Saved animated GIF: output/demo_visualizations/skeleton_animation.gif")
            
        except ImportError:
            print("  ⚠️  Pillow not available for GIF creation")
        
        plt.show()
        
    except Exception as e:
        print(f"  ❌ Error in 3D viewer: {e}")
        import traceback
        traceback.print_exc()

def calculate_skeleton_positions(offsets, parents, frame, total_frames):
    """Calculate skeleton joint positions with simple animation"""
    num_joints = len(parents)
    positions = np.zeros((num_joints, 3))
    
    # Animate the character with a walking motion
    t = frame / total_frames * 2 * np.pi
    
    # Root position (hips) - add some walking motion
    positions[0] = [0.1 * np.sin(t * 2), 0, 1.0 + 0.05 * np.cos(t * 4)]
    
    # Calculate other joint positions based on hierarchy
    for i in range(1, num_joints):
        parent_idx = parents[i]
        if parent_idx >= 0:
            # Add some animation to key joints
            offset = offsets[i].copy()
            
            # Animate arms (shoulders and elbows)
            if i in [16, 17, 18]:  # Left arm
                offset[1] += 0.1 * np.sin(t + np.pi)  # Swing opposite to right
            elif i in [20, 21]:  # Right arm
                offset[1] += 0.1 * np.sin(t)  # Swing with walking
            
            # Animate legs
            elif i in [1, 2, 3]:  # Left leg
                offset[2] += 0.05 * np.sin(t + np.pi)  # Step opposite to right
            elif i in [5, 6, 7]:  # Right leg
                offset[2] += 0.05 * np.sin(t)  # Step with walking
            
            # Add offset to parent position
            positions[i] = positions[parent_idx] + offset
    
    return positions

def create_web_viewer():
    """Create an HTML/JavaScript web viewer for BVH files"""
    print("\n🌐 Creating Web Viewer...")
    
    os.makedirs("output/web_viewer", exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSMT Animation Viewer</title>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            overflow: hidden; 
        }
        #container { width: 100vw; height: 100vh; }
        #controls { 
            position: absolute; 
            top: 20px; 
            left: 20px; 
            color: white; 
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-radius: 10px;
            min-width: 300px;
            backdrop-filter: blur(10px);
        }
        h3 { margin-top: 0; color: #4CAF50; }
        button { 
            margin: 5px; 
            padding: 12px 20px; 
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        button:hover { 
            background: linear-gradient(45deg, #45a049, #4CAF50);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        select, input[type="range"] { 
            margin: 5px; 
            padding: 8px; 
            background: #333; 
            color: white; 
            border: 1px solid #555;
            border-radius: 5px;
        }
        .control-group {
            margin: 15px 0;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        }
        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        #info {
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
    </style>
</head>
<body>
    <div id="container"></div>
    <div id="controls">
        <h3>🎬 RSMT Animation Viewer</h3>
        
        <div class="control-group">
            <label>Animation Controls:</label>
            <button onclick="loadDemoAnimation()">🎭 Load Demo Animation</button>
            <button onclick="playAnimation()">▶️ Play</button>
            <button onclick="pauseAnimation()">⏸️ Pause</button>
            <button onclick="resetAnimation()">⏮️ Reset</button>
        </div>
        
        <div class="control-group">
            <label>Speed: <span id="speedValue">1.0</span>x</label>
            <input type="range" id="speedSlider" min="0.1" max="3.0" step="0.1" value="1.0" onchange="updateSpeed()">
        </div>
        
        <div class="control-group">
            <label>Frame: <span id="frameValue">0</span></label>
            <input type="range" id="frameSlider" min="0" max="100" value="0" onchange="seekToFrame()">
        </div>
        
        <div class="control-group">
            <label>Camera:</label>
            <button onclick="resetCamera()">🎥 Reset View</button>
            <button onclick="toggleAutoRotate()">🔄 Auto Rotate</button>
        </div>
    </div>
    
    <div id="info">
        <strong>RSMT - Real-time Stylized Motion Transition</strong><br>
        Use mouse to orbit camera<br>
        Wheel to zoom, Right-click to pan
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, skeleton, clock;
        let isPlaying = false;
        let animationFrame = 0;
        let totalFrames = 60;
        let autoRotate = false;

        function init() {
            // Create scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x222222);

            // Create camera
            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(2, 1, 3);

            // Create renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            document.getElementById('container').appendChild(renderer.domElement);

            // Add lights
            const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(5, 5, 5);
            directionalLight.castShadow = true;
            scene.add(directionalLight);

            // Add ground
            const groundGeometry = new THREE.PlaneGeometry(10, 10);
            const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.receiveShadow = true;
            scene.add(ground);

            // Add orbit controls
            addOrbitControls();

            // Initialize clock
            clock = new THREE.Clock();

            // Start render loop
            animate();
            
            console.log("RSMT Viewer initialized successfully!");
        }

        function addOrbitControls() {
            // Simple orbit controls implementation
            let mouseDown = false;
            let mouseX = 0, mouseY = 0;
            
            renderer.domElement.addEventListener('mousedown', function(event) {
                mouseDown = true;
                mouseX = event.clientX;
                mouseY = event.clientY;
            });
            
            renderer.domElement.addEventListener('mouseup', function() {
                mouseDown = false;
            });
            
            renderer.domElement.addEventListener('mousemove', function(event) {
                if (mouseDown) {
                    const deltaX = event.clientX - mouseX;
                    const deltaY = event.clientY - mouseY;
                    
                    camera.position.x = Math.cos(deltaX * 0.01) * 3;
                    camera.position.z = Math.sin(deltaX * 0.01) * 3;
                    camera.position.y = Math.max(0.5, camera.position.y + deltaY * 0.01);
                    
                    camera.lookAt(0, 1, 0);
                    
                    mouseX = event.clientX;
                    mouseY = event.clientY;
                }
            });
        }

        function loadDemoAnimation() {
            // Create a demo skeleton animation
            createDemoSkeleton();
            console.log("Demo animation loaded!");
        }

        function createDemoSkeleton() {
            // Clear previous skeleton
            if (skeleton) {
                scene.remove(skeleton);
            }

            // Create skeleton group
            skeleton = new THREE.Group();
            
            // Define skeleton structure
            const joints = [
                {name: "hips", pos: [0, 1, 0], parent: -1},
                {name: "spine", pos: [0, 1.2, 0], parent: 0},
                {name: "chest", pos: [0, 1.4, 0], parent: 1},
                {name: "neck", pos: [0, 1.6, 0], parent: 2},
                {name: "head", pos: [0, 1.8, 0], parent: 3},
                {name: "leftShoulder", pos: [-0.2, 1.4, 0], parent: 2},
                {name: "leftElbow", pos: [-0.5, 1.2, 0], parent: 5},
                {name: "leftHand", pos: [-0.8, 1.0, 0], parent: 6},
                {name: "rightShoulder", pos: [0.2, 1.4, 0], parent: 2},
                {name: "rightElbow", pos: [0.5, 1.2, 0], parent: 8},
                {name: "rightHand", pos: [0.8, 1.0, 0], parent: 9},
                {name: "leftHip", pos: [-0.1, 0.9, 0], parent: 0},
                {name: "leftKnee", pos: [-0.1, 0.5, 0], parent: 11},
                {name: "leftFoot", pos: [-0.1, 0.1, 0], parent: 12},
                {name: "rightHip", pos: [0.1, 0.9, 0], parent: 0},
                {name: "rightKnee", pos: [0.1, 0.5, 0], parent: 14},
                {name: "rightFoot", pos: [0.1, 0.1, 0], parent: 15}
            ];

            // Create joint spheres and bones
            joints.forEach((joint, i) => {
                // Create joint sphere
                const geometry = new THREE.SphereGeometry(0.03, 8, 8);
                const material = new THREE.MeshPhongMaterial({ color: 0xff4444 });
                const sphere = new THREE.Mesh(geometry, material);
                sphere.position.set(...joint.pos);
                skeleton.add(sphere);

                // Create bone to parent
                if (joint.parent >= 0) {
                    const parentPos = joints[joint.parent].pos;
                    const boneGeometry = new THREE.CylinderGeometry(0.01, 0.01, 
                        Math.sqrt(
                            Math.pow(joint.pos[0] - parentPos[0], 2) +
                            Math.pow(joint.pos[1] - parentPos[1], 2) +
                            Math.pow(joint.pos[2] - parentPos[2], 2)
                        ));
                    const boneMaterial = new THREE.MeshPhongMaterial({ color: 0x4444ff });
                    const bone = new THREE.Mesh(boneGeometry, boneMaterial);
                    
                    // Position bone between joint and parent
                    bone.position.set(
                        (joint.pos[0] + parentPos[0]) / 2,
                        (joint.pos[1] + parentPos[1]) / 2,
                        (joint.pos[2] + parentPos[2]) / 2
                    );
                    
                    // Rotate bone to point from parent to joint
                    const direction = new THREE.Vector3(
                        joint.pos[0] - parentPos[0],
                        joint.pos[1] - parentPos[1],
                        joint.pos[2] - parentPos[2]
                    ).normalize();
                    bone.lookAt(new THREE.Vector3().addVectors(bone.position, direction));
                    bone.rotateX(Math.PI / 2);
                    
                    skeleton.add(bone);
                }
            });

            scene.add(skeleton);
        }

        function playAnimation() {
            isPlaying = true;
            console.log("Animation playing");
        }

        function pauseAnimation() {
            isPlaying = false;
            console.log("Animation paused");
        }

        function resetAnimation() {
            animationFrame = 0;
            isPlaying = true;
            document.getElementById('frameSlider').value = 0;
            document.getElementById('frameValue').textContent = 0;
            console.log("Animation reset");
        }

        function updateSpeed() {
            const slider = document.getElementById('speedSlider');
            const speed = parseFloat(slider.value);
            document.getElementById('speedValue').textContent = speed.toFixed(1);
        }

        function seekToFrame() {
            const slider = document.getElementById('frameSlider');
            animationFrame = parseInt(slider.value);
            document.getElementById('frameValue').textContent = animationFrame;
            updateSkeletonAnimation();
        }

        function resetCamera() {
            camera.position.set(2, 1, 3);
            camera.lookAt(0, 1, 0);
        }

        function toggleAutoRotate() {
            autoRotate = !autoRotate;
        }

        function updateSkeletonAnimation() {
            if (!skeleton) return;

            const t = (animationFrame / totalFrames) * Math.PI * 2;
            
            // Simple walking animation
            skeleton.children.forEach((child, i) => {
                if (child.isMesh && child.geometry.type === "SphereGeometry") {
                    // Animate specific joints
                    if (i === 6 || i === 7) { // Left arm
                        child.position.z = 0.1 * Math.sin(t + Math.PI);
                    } else if (i === 9 || i === 10) { // Right arm
                        child.position.z = 0.1 * Math.sin(t);
                    } else if (i === 12 || i === 13) { // Left leg
                        child.position.z = 0.05 * Math.sin(t + Math.PI);
                    } else if (i === 15 || i === 16) { // Right leg
                        child.position.z = 0.05 * Math.sin(t);
                    }
                }
            });
        }

        function animate() {
            requestAnimationFrame(animate);

            // Update animation
            if (isPlaying && skeleton) {
                const speed = parseFloat(document.getElementById('speedSlider').value);
                animationFrame = (animationFrame + speed) % totalFrames;
                
                document.getElementById('frameValue').textContent = Math.floor(animationFrame);
                document.getElementById('frameSlider').value = Math.floor(animationFrame);
                
                updateSkeletonAnimation();
            }

            // Auto rotate camera
            if (autoRotate) {
                const time = clock.getElapsedTime();
                camera.position.x = Math.cos(time * 0.5) * 3;
                camera.position.z = Math.sin(time * 0.5) * 3;
                camera.lookAt(0, 1, 0);
            }

            renderer.render(scene, camera);
        }

        // Handle window resize
        window.addEventListener('resize', function() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Initialize when page loads
        window.addEventListener('load', init);
    </script>
</body>
</html>'''
    
    with open("output/web_viewer/index.html", "w") as f:
        f.write(html_content)
    
    print("  ✅ Web viewer created: output/web_viewer/index.html")
    print("  🌐 To view: python -m http.server 8000")
    print("  🌐 Then open: http://localhost:8000/output/web_viewer/")

def create_blender_instructions():
    """Create instructions for viewing BVH files in Blender"""
    print("\n🎨 Creating Blender Instructions...")
    
    instructions = """# Viewing RSMT Results in Blender

## Quick Start Guide

### 1. Install Blender
- Download free from: https://www.blender.org/download/
- Install and launch Blender

### 2. Import BVH Animation
1. Delete the default cube (Select cube, press Delete)
2. Go to: File > Import > Motion Capture (.bvh)
3. Navigate to one of these BVH files:
   - `output/inference/test_pipeline.bvh`
   - `output/inference/final_test/final_test.bvh`
   - `output/inference/test_bvh_writer.bvh`

### 3. View Animation
1. Press SPACEBAR to play animation
2. Use mouse wheel to zoom
3. Middle mouse button to rotate view
4. Shift + middle mouse to pan

### 4. Enhance Visualization
1. In the 3D viewport, change shading to "Material Preview" or "Rendered"
2. Add a ground plane: Shift+A > Mesh > Plane, scale it up
3. Add lighting: Shift+A > Light > Sun

### 5. Export Animation
- File > Export > Alembic (.abc) for other software
- Or render as video: Rendering > Render Animation

## BVH Files Generated
"""
    
    # Find all BVH files
    bvh_files = []
    for root, dirs, files in os.walk("output"):
        for file in files:
            if file.endswith(".bvh"):
                bvh_files.append(os.path.join(root, file))
    
    for bvh in bvh_files:
        instructions += f"- {bvh}\n"
    
    instructions += """
## Tips
- BVH files contain skeleton animation data
- The character will appear as a stick figure initially
- You can add a mesh character and bind it to the skeleton for full character animation
- Blender's bone visualization shows the motion structure clearly
"""
    
    with open("output/demo_visualizations/blender_instructions.md", "w") as f:
        f.write(instructions)
    
    print("  ✅ Instructions saved: output/demo_visualizations/blender_instructions.md")

def main():
    """Main visualization setup function"""
    print("🎬 RSMT Results Visualizer")
    print("=" * 50)
    
    # Generate demo animations
    bvh_files = generate_demo_animations()
    
    # Create visualizations
    create_simple_3d_viewer()
    create_web_viewer()
    create_blender_instructions()
    
    print("\n🎉 Visualization Setup Complete!")
    print("=" * 50)
    print("\n📊 Available Visualization Options:")
    print("1. 📈 Static plots: output/demo_visualizations/skeleton_keyframes.png")
    print("2. 🎬 Animated GIF: output/demo_visualizations/skeleton_animation.gif")
    print("3. 🌐 Web viewer: output/web_viewer/index.html")
    print("4. 🎨 Blender files: See blender_instructions.md")
    
    print(f"\n📁 Generated {len(bvh_files)} BVH animation files ready for viewing!")
    
    print("\n🚀 Quick Start:")
    print("• For immediate viewing: Open the PNG/GIF files")
    print("• For interactive 3D: Run 'python -m http.server 8000' and visit the web viewer")
    print("• For professional results: Import BVH files into Blender")

if __name__ == "__main__":
    main()

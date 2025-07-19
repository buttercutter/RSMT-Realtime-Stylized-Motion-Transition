#!/usr/bin/env python3
"""
Web BVH Processor - Uses process_dataset.py functions without modification
Provides web API for single BVH file processing using existing RSMT infrastructure
"""

import os
import sys
import tempfile
import json
import shutil
from flask import Flask, request, jsonify
from flask import send_file, send_from_directory
from flask_cors import CORS


# Add the RSMT project to Python path
sys.path.append('../../')
sys.path.append('../../src')
sys.path.append('../../scripts/preprocessing')

# Import from the existing process_dataset.py (without modification)
import process_dataset
from src.Datasets.Style100Processor import StyleLoader, Swap100StyJoints, bvh_to_binary, save_skeleton
import src.utils.BVH_mod as BVH
from src.utils.motion_process import subsample
from src.Datasets.BaseLoader import BasedDataProcessor, BasedLoader, DataSetType, MotionDataLoader, WindowBasedLoader


from process_dataset import (
    processDeepPhaseForStyle100,
    processTransitionPhaseDatasetForStyle100
)


class SingleBVHProcessorUsingExistingFunctions:
    """
    Use existing RSMT functions directly by temporarily replacing their input source
    """

    def __init__(self):
        self.temp_dataset_dir = None
        self.original_dataset_path = None
        print("🔧 SingleBVHProcessorUsingExistingFunctions initialized")

    def _create_temp_dataset_with_single_bvh(self, bvh_content, style_name='neutral'):
        """
        Create a temporary dataset folder with just one BVH file
        So existing functions process only this single file
        """
        # Create temporary dataset directory
        self.temp_dataset_dir = tempfile.mkdtemp(prefix='single_bvh_dataset_')

        # Create the expected Style100 directory structure
        style_dir = os.path.join(self.temp_dataset_dir, 'Style100', style_name)
        os.makedirs(style_dir, exist_ok=True)

        # Write the single BVH file
        single_bvh_path = os.path.join(style_dir, 'single_motion.bvh')
        with open(single_bvh_path, 'w') as f:
            f.write(bvh_content)

        # Create a simple file list for the StyleLoader
        file_list_path = os.path.join(self.temp_dataset_dir, 'file_list.txt')
        with open(file_list_path, 'w') as f:
            f.write(f"{style_name}/single_motion.bvh\n")

        return single_bvh_path

    def _temporarily_redirect_dataset_path(self):
        """
        Temporarily redirect the StyleLoader to use our single-file dataset
        """
        # Get the original dataset path
        style_loader = StyleLoader()
        self.original_dataset_path = style_loader.data_path

        # Temporarily change to our single-file dataset
        style_loader.data_path = self.temp_dataset_dir
        StyleLoader.data_path = self.temp_dataset_dir  # Class-level change

        return style_loader

    def _restore_dataset_path(self):
        """
        Restore the original dataset path
        """
        if self.original_dataset_path:
            StyleLoader.data_path = self.original_dataset_path

    def _cleanup_temp_dataset(self):
        """
        Clean up temporary dataset directory
        """
        if self.temp_dataset_dir and os.path.exists(self.temp_dataset_dir):
            shutil.rmtree(self.temp_dataset_dir)
            self.temp_dataset_dir = None

    def process_single_bvh_using_processDeepPhaseForStyle100(self, bvh_content, style_name='neutral'):
        """
        Use the existing processDeepPhaseForStyle100 function directly
        by temporarily replacing its input source
        """
        try:
            # Step 1: Create temporary dataset with single BVH
            single_bvh_path = self._create_temp_dataset_with_single_bvh(bvh_content, style_name)

            # Step 2: Temporarily redirect dataset path
            self._temporarily_redirect_dataset_path()

            # Step 3: Call the EXISTING function directly
            # It will process our single BVH file instead of the entire Style100 dataset
            print("🧠 Calling processDeepPhaseForStyle100 on single BVH file...")
            processDeepPhaseForStyle100(62, 2)

            # Step 4: Load the generated features (they will be saved by the function)
            style_loader = StyleLoader()
            style_loader.data_path = self.temp_dataset_dir

            # The function saves features - load them
            try:
                features = style_loader.load_dataset("deep_phase_gv")
                return {
                    'success': True,
                    'model_type': 'deepphase',
                    'features': features,
                    'processing_method': 'Used existing processDeepPhaseForStyle100 function directly',
                    'single_file_path': single_bvh_path
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to load generated features: {str(e)}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Step 5: Restore original paths and cleanup
            self._restore_dataset_path()
            self._cleanup_temp_dataset()

    def process_single_bvh_using_processTransitionPhaseDatasetForStyle100(self, bvh_content, window_size, overlap, style_name='neutral'):
        """
        Use the existing processTransitionPhaseDatasetForStyle100 function directly
        by temporarily replacing its input source
        """
        try:
            # Step 1: Create temporary dataset with single BVH
            single_bvh_path = self._create_temp_dataset_with_single_bvh(bvh_content, style_name)

            # Step 2: Temporarily redirect dataset path
            self._temporarily_redirect_dataset_path()

            # Step 3: Call the EXISTING function directly
            print(f"🔄 Calling processTransitionPhaseDatasetForStyle100({window_size}, {overlap}) on single BVH file...")
            processTransitionPhaseDatasetForStyle100(window_size, overlap)

            # Step 4: Load the generated features
            style_loader = StyleLoader()
            style_loader.data_path = self.temp_dataset_dir

            # The function saves features - load them
            try:
                features = style_loader.load_dataset("transition_phase")
                return {
                    'success': True,
                    'model_type': f'transition_phase_w{window_size}_o{overlap}',
                    'features': features,
                    'window_size': window_size,
                    'overlap': overlap,
                    'processing_method': f'Used existing processTransitionPhaseDatasetForStyle100({window_size}, {overlap}) function directly',
                    'single_file_path': single_bvh_path
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to load generated features: {str(e)}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Step 5: Restore original paths and cleanup
            self._restore_dataset_path()
            self._cleanup_temp_dataset()


class SingleBVHProcessor:
    def __init__(self):
        self.function_processor = SingleBVHProcessorUsingExistingFunctions()
        print("🔧 SingleBVHProcessor initialized")

    def process_bvh_for_model(self, bvh_content, model_type, style_name='neutral'):
        """
        Process single BVH file using existing RSMT functions directly
        """
        try:
            if model_type == 'deepphase':
                return self.function_processor.process_single_bvh_using_processDeepPhaseForStyle100(
                    bvh_content, style_name
                )
            elif model_type == 'styleVAE':
                return self.function_processor.process_single_bvh_using_processTransitionPhaseDatasetForStyle100(
                    bvh_content, 61, 21, style_name  # manifold model parameters
                )
            elif model_type == 'transitionNet':
                return self.function_processor.process_single_bvh_using_processTransitionPhaseDatasetForStyle100(
                    bvh_content, 120, 0, style_name  # sampler model parameters
                )
            else:
                return {'success': False, 'error': f'Unknown model type: {model_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}


# Initialize the processor
processor = SingleBVHProcessor()

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/status')
def status():
    """Server status endpoint"""
    return jsonify({
        'server': 'RSMT Web BVH Processor',
        'status': 'running',
        'using_functions_from': 'process_dataset.py (unmodified)',
        'models': {
            'skeleton': {'status': 'ready', 'type': 'BVH skeleton processor'},
            'deephase': {'status': 'ready', 'type': 'Phase prediction model'},
            'stylevae': {'status': 'standby', 'type': 'Style encoding model'},
            'transitionnet': {'status': 'idle', 'type': 'Motion transition model'}
        },
        'ai_status': 'Models ready for processing',
        'models_using_ai': '3/3'
    })


@app.route('/process_bvh', methods=['POST'])
def process_bvh():
    """Process single BVH file using existing RSMT functions"""
    try:
        data = request.json
        bvh_content = data.get('bvh_content', '')
        model_type = data.get('model_type', 'deepphase')
        style = data.get('style', 'neutral')

        if not bvh_content:
            return jsonify({'error': 'No BVH content provided'}), 400

        # Use existing functions directly
        result = processor.process_bvh_for_model(bvh_content, model_type, style)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_windows', methods=['POST'])
def create_windows():
    """Create windowed data using process_dataset.py WindowBasedLoader"""
    try:
        data = request.json
        processed_data = data.get('processed_data', {})
        window_size = data.get('window_size', 65)
        overlap = data.get('overlap', 25)

        if not processed_data:
            return jsonify({'error': 'No processed data provided'}), 400

        print(f"🪟 Creating windows (size: {window_size}, overlap: {overlap})")

        # Use the processor that wraps process_dataset.py functions
        result = processor.create_windowed_data(processed_data, window_size, overlap)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result)

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/process_and_window', methods=['POST'])
def process_and_window():
    """Process BVH and create windows in one call"""
    try:
        data = request.json
        bvh_content = data.get('bvh_content', '')
        style = data.get('style', 'neutral')
        content = data.get('content', 'walking')
        window_size = data.get('window_size', 65)
        overlap = data.get('overlap', 25)

        if not bvh_content:
            return jsonify({'error': 'No BVH content provided'}), 400

        print(f"🔄 Full processing pipeline (style: {style}, window: {window_size})")

        # Step 1: Process BVH using process_dataset.py functions
        processed_data = processor.process_single_bvh_file(bvh_content, style, content)
        if 'error' in processed_data:
            return jsonify(processed_data), 500

        # Step 2: Create windows using process_dataset.py functions
        windowed_data = processor.create_windowed_data(processed_data, window_size, overlap)
        if 'error' in windowed_data:
            return jsonify(windowed_data), 500

        return jsonify({
            'processed_data': processed_data,
            'windowed_data': windowed_data,
            'processing_info': {
                'original_frames': processed_data['frame_count'],
                'window_count': windowed_data['window_count'],
                'window_size': window_size,
                'overlap': overlap,
                'using_functions_from': 'process_dataset.py'
            }
        })

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/transition_stats', methods=['POST'])
def transition_stats():
    """Generate transition statistics using TransitionProcessor from process_dataset.py"""
    try:
        data = request.json
        processed_data = data.get('processed_data', {})
        ref_id = data.get('ref_id', 0)
        ratio = data.get('ratio', 1.0)

        if not processed_data:
            return jsonify({'error': 'No processed data provided'}), 400

        print(f"📊 Generating transition statistics (ref_id: {ref_id}, ratio: {ratio})")

        # Use TransitionProcessor from process_dataset.py
        result = processor.process_with_transition_processor(processed_data, ref_id, ratio)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result)

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new endpoint
@app.route('/generate_deepphase_dataset', methods=['POST'])
def generate_deepphase_dataset():
    """Generate DeepPhase dataset using the original RSMT pipeline"""
    try:
        print("🔄 Generating DeepPhase dataset using processDeepPhaseForStyle100...")

        result = processor.process_deepphase_features()

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result)

    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/<filename>')
def serve_root_files(filename):
    """Serve BVH and ONNX files from the same directory as this script"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)

        # Check if file exists
        if os.path.exists(file_path):
            print(f"📁 Serving file: {filename}")
            return send_file(file_path)
        else:
            print(f"❌ File not found: {filename} in {script_dir}")
            # List files in directory for debugging
            files_in_dir = os.listdir(script_dir)
            print(f"📂 Files in directory: {files_in_dir}")
            return jsonify({'error': f'File not found: {filename}', 'directory': script_dir, 'files': files_in_dir}), 404

    except Exception as e:
        print(f"❌ Error serving file {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/rsmt_showcase_modern.html')
def serve_html():
    """Serve the main HTML interface"""
    try:
        # Look for the HTML file in the same directory as this script
        html_path = os.path.join(os.path.dirname(__file__), 'rsmt_showcase_modern.html')
        if os.path.exists(html_path):
            return send_file(html_path)
        else:
            return jsonify({'error': 'HTML file not found', 'path': html_path}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/showcase')
def serve_showcase():
    """Alternative route to serve the HTML interface"""
    return serve_html()

@app.route('/demo')
def serve_demo():
    """Demo route to serve the HTML interface"""
    return serve_html()

# Serve static files (for any additional CSS, JS, etc.)
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        return send_from_directory(static_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update the main route to provide navigation
@app.route('/')
def index():
    return jsonify({
        'server': 'RSMT Web BVH Processor',
        'description': 'Uses process_dataset.py functions without modification',
        'version': '1.0',
        'web_interface': '/rsmt_showcase_modern.html',
        'alternative_routes': ['/showcase', '/demo'],
        'api_endpoints': ['/process_bvh', '/create_windows', '/process_and_window', '/status'],
        'usage': 'Visit /rsmt_showcase_modern.html for the web interface'
    })


@app.route('/bvh-transition-system.html')
def serve_transition_system_html():
    """Serve the bvh-transition-system.html file"""
    try:
        html_path = os.path.join(os.path.dirname(__file__), 'bvh-transition-system.html')
        if os.path.exists(html_path):
            return send_file(html_path)
        else:
            return jsonify({'error': 'bvh-transition-system.html not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """Main function to start the web server"""
    import argparse

    parser = argparse.ArgumentParser(description='RSMT Web BVH Processor - Uses process_dataset.py functions')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port number (default: 8000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test', type=str, help='Test with a single BVH file')

    args = parser.parse_args()

    if args.test:
        # Test mode - process a single file
        if not os.path.exists(args.test):
            print(f"❌ BVH file not found: {args.test}")
            return

        print(f"🧪 Testing with {args.test}...")

        with open(args.test, 'r') as f:
            bvh_content = f.read()

        # Test processing
        result = processor.process_single_bvh_file(bvh_content)
        if 'error' in result:
            print(f"❌ Processing failed: {result['error']}")
            return

        # Test windowing
        windowed = processor.create_windowed_data(result)
        if 'error' in windowed:
            print(f"❌ Windowing failed: {windowed['error']}")
            return

        print(f"✅ Test successful!")
        print(f"   Frames: {result['frame_count']}")
        print(f"   Joints: {result['joint_count']}")
        print(f"   Windows: {windowed['window_count']}")

        # Save test results
        output_file = f"{os.path.splitext(args.test)[0]}_web_processed.json"
        with open(output_file, 'w') as f:
            json.dump({
                'processed_data': result,
                'windowed_data': windowed
            }, f, indent=2)
        print(f"💾 Results saved to: {output_file}")

    else:
        # Server mode
        print("🚀 Starting RSMT Web BVH Processor")
        print(f"📁 Using functions from: process_dataset.py (unmodified)")
        print(f"🌐 Server URL: http://{args.host}:{args.port}")
        print(f"🎭 Web Interface: http://{args.host}:{args.port}/rsmt_showcase_modern.html")
        print("📋 Available endpoints:")
        print("   GET  /           - Server info")
        print("   GET  /rsmt_showcase_modern.html - Web interface")
        print("   GET  /status     - Server status")
        print("   POST /process_bvh - Process BVH content")
        print("   POST /create_windows - Create windowed data")
        print("   POST /process_and_window - Full pipeline")
        print("   POST /transition_stats - Generate statistics")

        app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()

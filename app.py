import pytesseract
import os
from flask import Flask, request, jsonify, send_from_directory
import tempfile
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np
import logging
import re
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure Tesseract path
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Check if Tesseract exists at the specified path
if not os.path.exists(TESSERACT_PATH):
    logger.error(f"Tesseract not found at {TESSERACT_PATH}")
    raise RuntimeError(
        "Tesseract OCR is not installed or not found in the expected location.\n"
        "Please install it from: https://github.com/UB-Mannheim/tesseract/wiki"
    )

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

app = Flask(__name__)

def preprocess_image(image):
    """
    Preprocess image for better OCR accuracy
    """
    # Convert to numpy array if needed
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    # Convert back to PIL Image
    return Image.fromarray(gray)

def clean_and_structure_text(text):
    """
    Clean and structure the extracted text
    """
    # Remove extra whitespace and normalize
    text = ' '.join(text.split())
    
    # Split into sentences
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    # Remove special characters but keep basic punctuation
    sentences = [re.sub(r'[^a-zA-Z0-9\s,:-]', '', s).strip() for s in sentences]
    
    return sentences

def identify_topics(sentences):
    """
    Identify main topic and subtopics from sentences
    """
    if not sentences:
        return "No text found", []
    
    # First sentence is usually the main topic
    main_topic = sentences[0]
    
    # Process remaining sentences for subtopics
    all_words = ' '.join(sentences[1:]).lower().split()
    
    # Common words to exclude
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'can', 'could'}
    
    # Count word frequencies
    word_freq = defaultdict(int)
    for word in all_words:
        if (len(word) > 3 and  # Longer than 3 characters
            word not in stop_words and  # Not a stop word
            not word.isdigit()):  # Not just numbers
            word_freq[word] += 1
    
    # Get subtopics based on word frequency
    subtopics = []
    for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
        if len(subtopics) >= 5:  # Limit to top 5 subtopics
            break
        # Only add if not part of main topic
        if word not in main_topic.lower():
            subtopics.append(word)
    
    return main_topic, subtopics

def find_related_points(sentences, topic):
    """
    Find sentences related to a specific topic
    """
    related = []
    topic = topic.lower()
    
    for sentence in sentences:
        if topic in sentence.lower() and sentence not in related:
            # Clean and shorten the sentence if too long
            cleaned = ' '.join(sentence.split()[:10])  # Limit to first 10 words
            related.append(cleaned)
            if len(related) >= 2:  # Limit to 2 related points per topic
                break
    
    return related

def create_mind_map(text):
    """
    Create a hierarchical mind map from text
    """
    try:
        # Clean and structure the text
        sentences = clean_and_structure_text(text)
        if not sentences:
            return "- No readable text found in image"
        
        # Identify main topic and subtopics
        main_topic, subtopics = identify_topics(sentences)
        
        # Build mind map
        mind_map = [f"- {main_topic}"]
        
        # Add subtopics and their related points
        for subtopic in subtopics:
            # Capitalize subtopic
            subtopic_text = subtopic.capitalize()
            mind_map.append(f"  - {subtopic_text}")
            
            # Find and add related points
            related_points = find_related_points(sentences, subtopic)
            for point in related_points:
                if point and point.strip():
                    mind_map.append(f"    - {point.capitalize()}")
        
        return '\n'.join(mind_map)
    
    except Exception as e:
        logger.error(f"Error in mind map generation: {str(e)}")
        return "- Error creating mind map\n  - Please try again with clearer text"

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/process-image', methods=['POST'])
def process_image():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Check file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False, 
                'error': f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
            }), 400

        # Process the image
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            file.save(temp_file.name)
            
            try:
                # Read and preprocess image
                img = Image.open(temp_file.name)
                processed_img = preprocess_image(img)
                
                # Extract text using pytesseract with improved settings
                custom_config = r'--oem 3 --psm 6 -l eng'
                extracted_text = pytesseract.image_to_string(processed_img, config=custom_config)
                logger.debug(f"Extracted text length: {len(extracted_text)}")
                
                if not extracted_text.strip():
                    return jsonify({
                        'success': False, 
                        'error': 'No text could be extracted from the image. Please ensure the image contains clear, readable text.'
                    }), 400

                # Generate mind map from extracted text
                mind_map = create_mind_map(extracted_text)

                return jsonify({
                    'success': True,
                    'extracted_text': extracted_text,
                    'mind_map': mind_map
                })

            except Exception as img_error:
                logger.error(f"Image processing error: {str(img_error)}")
                return jsonify({
                    'success': False, 
                    'error': str(img_error)
                }), 500
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    logger.error(f"Error deleting temporary file: {str(e)}")

    except Exception as e:
        logger.error(f"General error in process_image: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error processing request: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
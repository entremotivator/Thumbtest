import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
import io

def add_thumbnail_overlay(video_path, thumbnail_path, output_path, position='top-right', size_ratio=0.2, duration_frames=90):
    """
    Add thumbnail as an overlay on the video using OpenCV
    
    Args:
        video_path (str): Path to input video file
        thumbnail_path (str): Path to thumbnail image
        output_path (str): Path for output video file
        position (str): Position of thumbnail overlay
        size_ratio (float): Size of thumbnail relative to video
        duration_frames (int): How many frames to show thumbnail
    
    Returns:
        bool: Success status
    """
    try:
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Load and resize thumbnail
        thumbnail = cv2.imread(thumbnail_path)
        if thumbnail is None:
            # Try loading with PIL and convert
            pil_img = Image.open(thumbnail_path)
            thumbnail = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Calculate thumbnail size
        thumb_width = int(width * size_ratio)
        thumb_height = int(thumb_width * thumbnail.shape[0] / thumbnail.shape[1])
        thumbnail = cv2.resize(thumbnail, (thumb_width, thumb_height))
        
        # Calculate position
        if position == 'top-right':
            x, y = width - thumb_width - 20, 20
        elif position == 'top-left':
            x, y = 20, 20
        elif position == 'bottom-right':
            x, y = width - thumb_width - 20, height - thumb_height - 20
        elif position == 'bottom-left':
            x, y = 20, height - thumb_height - 20
        else:  # center
            x, y = (width - thumb_width) // 2, (height - thumb_height) // 2
        
        # Ensure coordinates are valid
        x = max(0, min(x, width - thumb_width))
        y = max(0, min(y, height - thumb_height))
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        # Process each frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Add thumbnail overlay for the specified duration
            if frame_count < duration_frames:
                # Create a copy of the frame to modify
                overlay_frame = frame.copy()
                
                # Add thumbnail with some transparency
                alpha = 0.8  # Thumbnail opacity
                
                # Blend thumbnail with frame
                roi = overlay_frame[y:y+thumb_height, x:x+thumb_width]
                blended = cv2.addWeighted(roi, 1-alpha, thumbnail, alpha, 0)
                overlay_frame[y:y+thumb_height, x:x+thumb_width] = blended
                
                out.write(overlay_frame)
            else:
                out.write(frame)
            
            frame_count += 1
        
        # Release everything
        cap.release()
        out.release()
        
        return True
        
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return False

def create_thumbnail_intro(video_path, thumbnail_path, output_path, intro_duration_sec=3):
    """
    Create a video with thumbnail intro using OpenCV
    
    Args:
        video_path (str): Path to input video file
        thumbnail_path (str): Path to thumbnail image
        output_path (str): Path for output video file
        intro_duration_sec (int): Duration of intro in seconds
    
    Returns:
        bool: Success status
    """
    try:
        # Open video to get properties
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Load thumbnail
        thumbnail = cv2.imread(thumbnail_path)
        if thumbnail is None:
            # Try loading with PIL and convert
            pil_img = Image.open(thumbnail_path)
            thumbnail = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Resize thumbnail to match video dimensions
        thumbnail = cv2.resize(thumbnail, (width, height))
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Write intro frames (thumbnail)
        intro_frames = int(fps * intro_duration_sec)
        for _ in range(intro_frames):
            out.write(thumbnail)
        
        # Write original video frames
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
        
        # Release everything
        cap.release()
        out.release()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating intro video: {str(e)}")
        return False

def extract_thumbnail_from_video(video_path, position=0.1):
    """Extract a frame from video as thumbnail"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_number = int(total_frames * position)
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB for PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
        
        return None
        
    except:
        return None

def get_video_info(video_path):
    """Get basic video information using OpenCV"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        return {
            'duration': duration,
            'fps': fps,
            'width': width,
            'height': height,
            'total_frames': frame_count
        }
    except:
        return None

def main():
    st.title("🎬 Video Thumbnail Creator")
    st.write("Add custom thumbnails to your videos using OpenCV")
    
    st.info("📱 This app uses OpenCV and works on Streamlit Cloud")
    
    # Sidebar for mode selection
    st.sidebar.title("🎯 Mode Selection")
    mode = st.sidebar.radio(
        "Choose what you want to do:",
        ["Add Custom Thumbnail", "Extract Thumbnail from Video"]
    )
    
    if mode == "Add Custom Thumbnail":
        # Create two columns for file uploads
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📹 Upload Video")
            video_file = st.file_uploader(
                "Choose a video file",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Supported formats: MP4, AVI, MOV, MKV"
            )
        
        with col2:
            st.subheader("🖼️ Upload Thumbnail")
            thumbnail_file = st.file_uploader(
                "Choose a thumbnail image",
                type=['jpg', 'jpeg', 'png', 'bmp'],
                help="Supported formats: JPG, PNG, BMP"
            )
        
        if video_file is not None and thumbnail_file is not None:
            # Display file information
            st.success("✅ Both files uploaded successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Video Info:**")
                st.write(f"📁 Name: {video_file.name}")
                st.write(f"📊 Size: {video_file.size / (1024*1024):.2f} MB")
            
            with col2:
                st.write("**Thumbnail Info:**")
                st.write(f"📁 Name: {thumbnail_file.name}")
                st.write(f"📊 Size: {thumbnail_file.size / 1024:.2f} KB")
            
            # Save files to temporary locations
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as tmp_video:
                tmp_video.write(video_file.read())
                video_path = tmp_video.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{thumbnail_file.name.split('.')[-1]}") as tmp_thumb:
                tmp_thumb.write(thumbnail_file.read())
                thumbnail_path = tmp_thumb.name
            
            # Display thumbnail preview
            thumbnail_image = Image.open(thumbnail_path)
            st.image(thumbnail_image, caption="Thumbnail Preview", width=200)
            
            # Get video information
            video_info = get_video_info(video_path)
            if video_info:
                st.subheader("📊 Video Details")
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.metric("Duration", f"{video_info['duration']:.1f}s")
                    st.metric("FPS", f"{video_info['fps']:.1f}")
                
                with info_col2:
                    st.metric("Resolution", f"{video_info['width']}x{video_info['height']}")
                    st.metric("Total Frames", f"{video_info['total_frames']:,}")
            
            # Settings
            st.subheader("⚙️ Thumbnail Settings")
            
            thumbnail_mode = st.radio(
                "Choose how to add your thumbnail:",
                options=["Intro Screen", "Overlay"],
                help="Intro Screen: Shows thumbnail before video starts\nOverlay: Shows thumbnail as overlay during video"
            )
            
            if thumbnail_mode == "Intro Screen":
                intro_duration = st.slider(
                    "Intro Duration (seconds)",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="How long to show the thumbnail before the video starts"
                )
            else:  # Overlay mode
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    overlay_position = st.selectbox(
                        "Overlay Position",
                        options=['top-right', 'top-left', 'bottom-right', 'bottom-left', 'center'],
                        index=0
                    )
                
                with col2:
                    overlay_size = st.slider(
                        "Overlay Size (%)",
                        min_value=10,
                        max_value=40,
                        value=20,
                        help="Size of overlay relative to video width"
                    )
                
                with col3:
                    overlay_duration = st.slider(
                        "Overlay Duration (seconds)",
                        min_value=1,
                        max_value=min(15, int(video_info['duration']) if video_info else 15),
                        value=5,
                        help="How long to show the overlay from the start"
                    )
            
            # Process video button
            if st.button("🎬 Create Video with Thumbnail", type="primary"):
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🎬 Processing video... Please wait")
                progress_bar.progress(25)
                
                try:
                    # Create output file
                    output_filename = f"thumbnail_{video_file.name.replace('.', '_')}.mp4"
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
                        output_path = tmp_output.name
                    
                    progress_bar.progress(50)
                    
                    # Process video based on selected mode
                    if thumbnail_mode == "Intro Screen":
                        status_text.text("📽️ Adding intro thumbnail...")
                        success = create_thumbnail_intro(video_path, thumbnail_path, output_path, intro_duration)
                    else:
                        status_text.text("🎯 Adding thumbnail overlay...")
                        duration_frames = int(video_info['fps'] * overlay_duration) if video_info else 150
                        success = add_thumbnail_overlay(
                            video_path, 
                            thumbnail_path, 
                            output_path, 
                            overlay_position, 
                            overlay_size/100,
                            duration_frames
                        )
                    
                    progress_bar.progress(75)
                    
                    if success and os.path.exists(output_path):
                        progress_bar.progress(100)
                        status_text.text("✅ Video processed successfully!")
                        
                        # Get file size
                        output_size = os.path.getsize(output_path)
                        st.success(f"🎉 Video created! Size: {output_size / (1024*1024):.2f} MB")
                        
                        # Read processed video for download
                        with open(output_path, 'rb') as f:
                            video_bytes = f.read()
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Video with Thumbnail",
                            data=video_bytes,
                            file_name=output_filename,
                            mime="video/mp4"
                        )
                        
                        # Clean up output file
                        try:
                            os.unlink(output_path)
                        except:
                            pass
                        
                    else:
                        progress_bar.progress(0)
                        status_text.text("❌ Processing failed")
                        st.error("❌ Failed to process video. Please try a different video format.")
                
                except Exception as e:
                    progress_bar.progress(0)
                    status_text.text("❌ Processing failed")
                    st.error(f"Error processing video: {str(e)}")
            
            # Clean up temporary files
            try:
                for path in [video_path, thumbnail_path]:
                    if os.path.exists(path):
                        os.unlink(path)
            except:
                pass
        
        elif video_file is not None:
            st.info("📹 Video uploaded. Please also upload a thumbnail image.")
        elif thumbnail_file is not None:
            st.info("🖼️ Thumbnail uploaded. Please also upload a video file.")
    
    else:  # Extract Thumbnail mode
        st.subheader("📹 Extract Thumbnail from Video")
        
        video_file = st.file_uploader(
            "Choose a video file to extract thumbnail from",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a video to extract a frame as thumbnail"
        )
        
        if video_file is not None:
            st.success(f"✅ Video uploaded: {video_file.name}")
            
            # Save video to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as tmp_video:
                tmp_video.write(video_file.read())
                video_path = tmp_video.name
            
            # Get video info
            video_info = get_video_info(video_path)
            if video_info:
                st.write(f"📊 Duration: {video_info['duration']:.1f}s | Resolution: {video_info['width']}x{video_info['height']}")
                
                # Frame position selector
                frame_position = st.slider(
                    "Select frame position to extract",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.05,
                    help="0.0 = start, 0.5 = middle, 1.0 = end"
                )
                
                if st.button("🖼️ Extract Thumbnail", type="primary"):
                    with st.spinner("Extracting thumbnail..."):
                        thumbnail = extract_thumbnail_from_video(video_path, frame_position)
                        
                        if thumbnail:
                            st.success("✅ Thumbnail extracted!")
                            st.image(thumbnail, caption=f"Extracted from {video_file.name}", width=400)
                            
                            # Convert to bytes for download
                            img_buffer = io.BytesIO()
                            thumbnail.save(img_buffer, format='PNG')
                            img_bytes = img_buffer.getvalue()
                            
                            # Download button
                            filename = f"thumbnail_{video_file.name.split('.')[0]}.png"
                            st.download_button(
                                label="💾 Download Thumbnail",
                                data=img_bytes,
                                file_name=filename,
                                mime="image/png"
                            )
                        else:
                            st.error("❌ Failed to extract thumbnail")
            
            # Clean up
            try:
                os.unlink(video_path)
            except:
                pass
    
    # Instructions
    st.subheader("📋 Instructions")
    if mode == "Add Custom Thumbnail":
        st.markdown("""
        1. **Upload both video and thumbnail files**
        2. **Choose thumbnail mode**:
           - **Intro Screen**: Thumbnail shows for X seconds before video starts
           - **Overlay**: Thumbnail appears as watermark during video
        3. **Configure settings** for position, size, and duration
        4. **Click "Create Video"** and wait for processing
        5. **Download your new video** with embedded thumbnail
        """)
    else:
        st.markdown("""
        1. **Upload a video file**
        2. **Use the slider** to select which frame to extract
        3. **Click "Extract Thumbnail"** to generate the image
        4. **Download the thumbnail** as a PNG file
        """)
    
    # Technical info
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        - **Processing**: Uses OpenCV for video manipulation
        - **Output Format**: MP4 with MPEG-4 codec
        - **Compatibility**: Works on Streamlit Cloud with standard libraries
        - **Performance**: Processing time depends on video length and size
        - **Limitations**: Some advanced video codecs may not be supported
        """)

if __name__ == "__main__":
    main()

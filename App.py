import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import io

def create_thumbnail_overlay(video_path, thumbnail_path, output_path, position='top-right', size_ratio=0.2, duration_seconds=3):
    """
    Add thumbnail as an overlay on the video using MoviePy
    
    Args:
        video_path (str): Path to input video file
        thumbnail_path (str): Path to thumbnail image
        output_path (str): Path for output video file
        position (str): Position of thumbnail overlay
        size_ratio (float): Size of thumbnail relative to video
        duration_seconds (int): How long to show thumbnail (from start)
    
    Returns:
        bool: Success status
    """
    try:
        # Load video
        video = VideoFileClip(video_path)
        
        # Load and resize thumbnail
        thumbnail_img = Image.open(thumbnail_path)
        
        # Calculate thumbnail size
        video_width, video_height = video.size
        thumb_width = int(video_width * size_ratio)
        thumb_height = int(thumb_width * thumbnail_img.height / thumbnail_img.width)
        
        # Resize thumbnail
        thumbnail_img = thumbnail_img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        
        # Convert PIL to numpy array
        thumb_array = np.array(thumbnail_img)
        
        # Create ImageClip from thumbnail
        thumbnail_clip = ImageClip(thumb_array, duration=min(duration_seconds, video.duration))
        
        # Set position
        if position == 'top-right':
            thumbnail_clip = thumbnail_clip.set_position(('right', 'top')).set_margin(20)
        elif position == 'top-left':
            thumbnail_clip = thumbnail_clip.set_position(('left', 'top')).set_margin(20)
        elif position == 'bottom-right':
            thumbnail_clip = thumbnail_clip.set_position(('right', 'bottom')).set_margin(20)
        elif position == 'bottom-left':
            thumbnail_clip = thumbnail_clip.set_position(('left', 'bottom')).set_margin(20)
        elif position == 'center':
            thumbnail_clip = thumbnail_clip.set_position('center')
        
        # Composite video with thumbnail overlay
        final_video = CompositeVideoClip([video, thumbnail_clip])
        
        # Write the result
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Clean up
        video.close()
        final_video.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return False

def create_intro_thumbnail(video_path, thumbnail_path, output_path, intro_duration=3):
    """
    Add thumbnail as intro screen before the video starts
    
    Args:
        video_path (str): Path to input video file
        thumbnail_path (str): Path to thumbnail image
        output_path (str): Path for output video file
        intro_duration (int): Duration of intro thumbnail in seconds
    
    Returns:
        bool: Success status
    """
    try:
        # Load video
        video = VideoFileClip(video_path)
        
        # Load thumbnail
        thumbnail_img = Image.open(thumbnail_path)
        
        # Resize thumbnail to match video dimensions
        video_width, video_height = video.size
        thumbnail_img = thumbnail_img.resize((video_width, video_height), Image.Resampling.LANCZOS)
        
        # Convert PIL to numpy array
        thumb_array = np.array(thumbnail_img)
        
        # Create intro clip from thumbnail
        intro_clip = ImageClip(thumb_array, duration=intro_duration)
        
        # Concatenate intro with video
        from moviepy.editor import concatenate_videoclips
        final_video = concatenate_videoclips([intro_clip, video])
        
        # Write the result
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Clean up
        video.close()
        final_video.close()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating intro video: {str(e)}")
        return False

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
    st.write("Upload a video and a custom thumbnail image to create a new video with your thumbnail")
    
    st.info("📱 This app is optimized for Streamlit Cloud and uses MoviePy for video processing")
    
    # Create two columns for file uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📹 Upload Video")
        video_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'avi', 'mov', 'mkv', 'wmv'],
            help="Supported formats: MP4, AVI, MOV, MKV, WMV"
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
            help="Intro Screen: Shows thumbnail for a few seconds before video starts\nOverlay: Shows thumbnail as a small overlay during part of the video"
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
                    max_value=50,
                    value=20,
                    help="Size of overlay relative to video width"
                )
            
            with col3:
                overlay_duration = st.slider(
                    "Overlay Duration (seconds)",
                    min_value=1,
                    max_value=min(10, int(video_info['duration']) if video_info else 10),
                    value=3,
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
                output_filename = f"thumbnail_{video_file.name}"
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_output:
                    output_path = tmp_output.name
                
                progress_bar.progress(50)
                
                # Process video based on selected mode
                if thumbnail_mode == "Intro Screen":
                    status_text.text("📽️ Adding intro thumbnail...")
                    success = create_intro_thumbnail(video_path, thumbnail_path, output_path, intro_duration)
                else:
                    status_text.text("🎯 Adding thumbnail overlay...")
                    success = create_thumbnail_overlay(
                        video_path, 
                        thumbnail_path, 
                        output_path, 
                        overlay_position, 
                        overlay_size/100, 
                        overlay_duration
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
                    st.error("❌ Failed to process video. Please try again with different settings.")
            
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
    
    # Instructions
    st.subheader("📋 How to Use")
    st.markdown("""
    1. **Upload a video file** - MP4, AVI, MOV, MKV, or WMV format
    2. **Upload a thumbnail image** - JPG, PNG, or BMP format
    3. **Choose thumbnail mode**:
       - **Intro Screen**: Your thumbnail appears for a few seconds before the video starts
       - **Overlay**: Your thumbnail appears as a small overlay during the beginning of the video
    4. **Configure settings** for your chosen mode
    5. **Click "Create Video"** to process
    6. **Download your new video** with the thumbnail included
    """)
    
    # Example use cases
    st.subheader("💡 Use Cases")
    st.markdown("""
    - **Social Media**: Add custom thumbnails to your videos before uploading
    - **Branding**: Include your logo or brand image as an intro or overlay
    - **Previews**: Show a preview image before your video content starts
    - **Professional**: Add title cards or custom graphics to your videos
    """)
    
    # Technical info
    with st.expander("🔧 Technical Details"):
        st.markdown("""
        - **Processing**: Uses MoviePy (Python-based) for video editing
        - **Output Format**: MP4 with H.264 codec
        - **Quality**: Maintains original video quality
        - **Cloud Compatible**: Works on Streamlit Cloud without external dependencies
        - **File Size**: Output file will be larger due to added thumbnail content
        """)

if __name__ == "__main__":
    main()

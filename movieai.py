import os
import json
import streamlit as st
from groq import Groq
# Requests and pandas imports are kept but unused in the current core logic.

st.set_page_config(page_title="AI 2 Movie Script Generator", page_icon="🎬", layout="wide")

# Initialize session state for script generation
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""

# --- Movie Shot List (from your image) ---
MOVIE_SHOT_TYPES = [
    "Master/Establishing Shot", "Full Shot", "Medium Shot", "Medium Close-Up Shot", 
    "Close-Up Shot", "Extreme Close-Up Shot", "Extreme Angle", "Bird's-Eye View", 
    "Low Angle", "Depth Staging", "Planar Staging", "Pull Back Reveal", 
    "Contract Dolly", "Point of View (POV)", "Dark Voyeur", "Shadow", 
    "Follow Shot", "Over the shoulder"
]

# --- Core AI Script Generation Function ---
def generate_creative_content(movie_type, output_format, video_length_style, groq_client_instance, model_name):
    """
    Uses the Groq model to generate creative content based on movie type, output format,
    video length/style, and incorporating various shot types.
    """
    
    shot_instructions = "Please incorporate a variety of camera shots and angles from this list into your scene descriptions and stage directions: " + ", ".join(MOVIE_SHOT_TYPES) + "."
    
    # Adjust prompt based on output format
    format_specific_instructions = ""
    if output_format == "Storyboard Text":
        format_specific_instructions = "Focus on visual descriptions for each shot, suitable for a text-based storyboard. Describe key visuals and camera movements. Do not include dialogue unless essential for a scene beat. For each 'panel', briefly describe the shot and action. Use clear section headers for each panel."
    elif output_format == "Dialog Script":
        format_specific_instructions = "Prioritize character dialogue and essential action beats, with minimal camera directions. Format as a standard dialogue-focused screenplay."
    elif output_format == "Shooting Script":
        format_specific_instructions = "Include detailed scene headings, character dialogue, specific action descriptions, and explicit camera shot descriptions. Format as a comprehensive shooting script, adhering to standard industry conventions (CAPS for characters/headings, proper indentation)."

    # Adjust prompt based on video length/style
    length_specific_instructions = ""
    if video_length_style == "TikTok (Short Video - ~30s)":
        length_specific_instructions = "Keep the scene extremely short and impactful, ideal for a quick social media video. Aim for 3-5 concise shots/dialogue exchanges."
    elif video_length_style == "YouTube (Medium Video - 1-3 min)":
        length_specific_instructions = "Generate a single, coherent scene suitable for a short online video. Aim for 5-10 shots/dialogue exchanges."
    elif video_length_style == "Film Scene (Longer Scene - 3+ min)":
        length_specific_instructions = "Develop a more detailed and expansive scene, suitable for a segment of a film. Include more character interaction and environmental detail. Aim for 10-20 shots/dialogue exchanges. The scene should be long enough to fill 3+ minutes."

    prompt = f"""
    You are an AI writer and director. Your task is to generate creative content for a single scene
    based on the user's requested movie type, output format, and desired video length/style.
    
    Movie Type: {movie_type}
    Output Format: {output_format}
    Video Length/Style: {video_length_style}
    
    {shot_instructions}
    
    {format_specific_instructions}
    {length_specific_instructions}
    
    Ensure the output is well-structured according to the chosen format.
    """
    
    try:
        with st.spinner(f"Generating {output_format} for a {video_length_style} {movie_type} scene..."):
            response = groq_client_instance.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85, 
                max_tokens=2500,
            )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Improved error display for API issues
        error_message = str(e)
        if "organization_restricted" in error_message:
            st.error("🚨 API Access Restricted: Your Groq organization has been restricted. Please contact Groq support.")
        elif "Invalid API Key" in error_message:
            st.error("🔑 Invalid API Key: Please verify your `GROQ_API_KEY` in environment variables or secrets.")
        else:
            st.error(f"Error generating content: {e}")
        return "Failed to generate content due to an external API error."

# --- Main App ---
def main():
    st.markdown("""
    <style>
        .block-container { padding-left: 2rem; padding-right: 2rem; }
        .stAlert { margin-top: 1rem; }
        /* Style for the generated script display to look like a script page */
        pre {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            white-space: pre-wrap; /* Ensures long lines wrap */
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("🎬 AI 2 Movie Scene Generator")
    st.markdown("AI-powered tool to generate detailed scene content based on genre, format, and video style.")

    # Sidebar Configuration
    st.sidebar.image("2.png", caption="Lights, Camera, Action!", use_container_width=True)
    st.sidebar.header("⚙️ Settings")
    
    # Groq API Key check 
    groq_api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    
    groq_client_instance = None
    if not groq_api_key:
        st.error("⚠️ Groq API key not found. Please set `GROQ_API_KEY` as an environment variable or in Streamlit secrets (`.streamlit/secrets.toml`).")
        # Do not st.stop() here, allow the UI to load so the user can see the error.
        groq_client_instance = None
    else:
        try:
            groq_client_instance = Groq(api_key=groq_api_key)
        except Exception as e:
            st.error(f"Failed to initialize Groq client: {e}")
            groq_client_instance = None

    model_name = st.sidebar.selectbox(
        "AI Model:",
        ["llama-3.3-70b-versatile","openai/gpt-oss-120b","mixtral-8x7b-32768", "llama-3.1-70b-versatile", "gemma-7b-it"],
        help="Choose the AI model for generation. Larger models generally offer better quality."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🤖 AI Features:**")
    st.sidebar.markdown("✓ Generate diverse scene content (Storyboard, Dialog, Shooting Script)")
    st.sidebar.markdown("✓ Customize for different video lengths/styles (TikTok, YouTube, Film)")
    st.sidebar.markdown("✓ Tailored to your chosen movie type and cinematic shot types")
    st.sidebar.caption("Built with 💡 Streamlit + Groq | DW 2025")
    
    st.sidebar.markdown("---")
    st.sidebar.header("🎬 Shot List Reference")
    st.sidebar.markdown("The AI will incorporate a variety of these shot types:")
    for shot in MOVIE_SHOT_TYPES:
        st.sidebar.write(f"- {shot}")

    # Main Interface for Script Generation
    st.header("Define Your Scene Parameters")
        
    # User input for movie type
    movie_type_input = st.text_input(
        "What kind of movie scene would you like?",
        placeholder="e.g., Sci-Fi Thriller, Romantic Comedy, Fantasy Adventure, Horror",
        key="movie_type_input"
    )

    # New options for output format and video length/style
    col1, col2 = st.columns(2)
    with col1:
        output_format_input = st.selectbox(
            "Select Output Format:",
            ["Shooting Script", "Dialog Script", "Storyboard Text"], # Reordered to put most detailed first
            help="Choose how the content is formatted: visual descriptions, dialogue, or detailed script."
        )
    with col2:
        video_length_style_input = st.selectbox(
            "Select Video Length/Style:",
            ["Film Scene (Longer Scene - 3+ min)", "YouTube (Medium Video - 1-3 min)", "TikTok (Short Video - ~30s)"],
            help="Specify the intended length and style of the video for the scene."
        )

    # Generate Script button
    if st.button("Generate Scene Content", type="primary", key="generate_script_button"):
        if not groq_client_instance:
             st.error("Cannot run generation. Please resolve the API Key issue displayed above.")
        elif movie_type_input:
            st.session_state.generated_script = generate_creative_content(
                movie_type_input,
                output_format_input,
                video_length_style_input,
                groq_client_instance,
                model_name
            )
        else:
            st.warning("Please enter a movie type to generate content.")

    # Display the generated script
    if st.session_state.generated_script:
        st.subheader(f"Generated Content: ({output_format_input})")
        # Use simple markdown for display, rely on the custom CSS for styling the <pre> block
        st.code(st.session_state.generated_script, language='text')

if __name__ == "__main__":
    main()
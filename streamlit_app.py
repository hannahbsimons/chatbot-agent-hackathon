import streamlit as st
from openai import OpenAI
from PIL import Image
import os

# Show title and description.
st.title("💬 Chatbot with Image Upload")
st.write(
    "This is our hackathon project where users can send a screenshot along with a text-based request. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Step 1: Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Step 2: Prompt user to upload an image file.
    uploaded_file = st.file_uploader("Upload a screenshot or image file", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Save the uploaded image to disk
        save_path = os.path.join("uploads", uploaded_file.name)
        os.makedirs("uploads", exist_ok=True)  # Ensure the directory exists
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File saved to {save_path}")

        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        # Step 3: Ask user to enter a prompt related to the uploaded image.
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display existing chat messages.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message.
        if prompt := st.chat_input("Ask our agent about your uploaded image!"):
            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response to the chat and store it.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

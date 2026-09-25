
import os
import json
import streamlit as st
from groq import Groq


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MailMind AI",
    page_icon="✉️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #fff7fc;
}

.block-container {
    max-width: 1100px;
    padding-top: 3rem;
}

.hero {
    text-align: center;
    padding: 30px 10px 25px 10px;
}

.hero h1 {
    font-size: 48px;
    font-weight: 800;
    margin-bottom: 10px;
    color: #8b3d8f;
}

.hero p {
    font-size: 18px;
    color: #a05a8d;
}

.card {
    background: #ffffff;
    border: 1px solid #f0c8e5;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(180, 80, 150, 0.08);
}

.result-card {
    background: #fffaff;
    border: 1px solid #dfb6dc;
    border-radius: 18px;
    padding: 25px;
    margin-top: 25px;
    box-shadow: 0 8px 25px rgba(180, 80, 150, 0.08);
}

.small-label {
    color: #9a4d91;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 5px;
}

.footer {
    text-align: center;
    color: #a8789f;
    padding: 40px 0 20px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# GROQ API
# ============================================================

api_key = os.getenv("MAILMIND_GROQ_API_KEY")

if not api_key:
    st.error("MAILMIND_GROQ_API_KEY is missing.")
    st.stop()

client = Groq(api_key=api_key)


# ============================================================
# SESSION STATE
# ============================================================

if "subject" not in st.session_state:
    st.session_state.subject = ""

if "body" not in st.session_state:
    st.session_state.body = ""

if "history" not in st.session_state:
    st.session_state.history = []


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">
    <h1>✉️ MailMind AI</h1>
    <p>Write better emails in seconds.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# INPUT CARD
# ============================================================

st.markdown('<div class="card">', unsafe_allow_html=True)


# ------------------------------------------------------------
# LANGUAGE + EMAIL PURPOSE
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    language = st.selectbox(
        "Language",
        [
            "English",
            "Urdu",
            "Roman Urdu",
            "Arabic",
            "Spanish",
            "French",
            "German"
        ]
    )


with col2:

    email_purpose = st.selectbox(
        "Email Purpose",
        [
            "General",
            "Job Application",
            "Leave Request",
            "Follow-up",
            "Meeting",
            "Request",
            "Thank You",
            "Apology",
            "Complaint",
            "Invitation",
            "Sales / Business",
            "Customer Support"
        ]
    )


# ------------------------------------------------------------
# RECIPIENT + TONE
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    recipient = st.selectbox(
        "Recipient",
        [
            "Manager",
            "HR",
            "Client",
            "Customer",
            "Teacher / Professor",
            "Colleague",
            "Employer",
            "Business Partner",
            "Friend",
            "General"
        ]
    )


with col2:

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Friendly",
            "Formal",
            "Casual",
            "Polite",
            "Persuasive",
            "Apologetic",
            "Confident"
        ]
    )


# ------------------------------------------------------------
# LENGTH
# ------------------------------------------------------------

length = st.selectbox(
    "Email Length",
    [
        "Short",
        "Medium",
        "Long"
    ]
)


# ------------------------------------------------------------
# USER REQUEST
# ------------------------------------------------------------

user_request = st.text_area(
    "What do you want to write?",
    placeholder="Example: Write an email to my manager requesting two days of leave because of a family event.",
    height=160
)


generate = st.button(
    "✨ Generate Email",
    use_container_width=True
)


st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# GENERATE EMAIL
# ============================================================

if generate:

    if not user_request.strip():

        st.warning(
            "Please describe the email you want to write."
        )

    else:

        prompt = f"""
You are an expert professional email writer.

Create an email using the following information.

Language:
{language}

Email Purpose:
{email_purpose}

Recipient:
{recipient}

Tone:
{tone}

Email Length:
{length}

User Request:
{user_request}

IMPORTANT:

- Write the email completely in the selected language.
- Match the selected tone.
- Make it appropriate for the selected recipient.
- Follow the selected purpose.
- Follow the selected length.
- Create a clear subject.
- Make the email natural and ready to send.
- Do not invent unnecessary personal information.
- Return ONLY one valid JSON object.
- Do not write anything before or after the JSON.

Return exactly:

{{
    "subject": "Short and relevant email subject",
    "body": "Complete email body"
}}
"""


        try:

            with st.spinner("Writing your email..."):

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a professional email writer. "
                                "Return ONLY a valid JSON object "
                                "containing exactly two fields: "
                                "subject and body."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.7,
                    max_tokens=800
                )


            # ------------------------------------------------
            # GET RESPONSE
            # ------------------------------------------------

            result = response.choices[0].message.content.strip()


            # ------------------------------------------------
            # REMOVE MARKDOWN
            # ------------------------------------------------

            result = result.replace(
                "```json",
                ""
            )

            result = result.replace(
                "```",
                ""
            )

            result = result.strip()


            # ------------------------------------------------
            # EXTRACT JSON
            # ------------------------------------------------

            start = result.find("{")
            end = result.rfind("}")


            if start == -1 or end == -1:

                st.error(
                    "The AI did not return a valid JSON object."
                )

                st.code(result)

                st.stop()


            result = result[
                start:end + 1
            ]


            # ------------------------------------------------
            # PARSE JSON
            # ------------------------------------------------

            data = json.loads(result)


            # ------------------------------------------------
            # GET SUBJECT AND BODY
            # ------------------------------------------------

            subject = str(
                data.get("subject", "")
            ).strip()

            body = str(
                data.get("body", "")
            ).strip()


            if not subject or not body:

                st.error(
                    "The AI returned an incomplete email."
                )

                st.stop()


            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            st.session_state.subject = subject

            st.session_state.body = body


            # ------------------------------------------------
            # SAVE HISTORY
            # ------------------------------------------------

            st.session_state.history.insert(

                0,

                {
                    "subject": subject,
                    "body": body,
                    "purpose": email_purpose,
                    "recipient": recipient,
                    "tone": tone,
                    "language": language,
                    "length": length
                }
            )


            st.session_state.history = (
                st.session_state.history[:10]
            )


        except json.JSONDecodeError:

            st.error(
                "The AI response was not valid JSON."
            )

            st.code(result)


        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )


# ============================================================
# RESULT
# ============================================================

if (
    st.session_state.subject
    and st.session_state.body
):

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True
    )

    st.subheader(
        "Generated Email"
    )


    # --------------------------------------------------------
    # SUBJECT
    # --------------------------------------------------------

    st.markdown(
        '<div class="small-label">SUBJECT</div>',
        unsafe_allow_html=True
    )

    st.text_input(
        "Subject",
        value=st.session_state.subject,
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    st.markdown(
        '<div class="small-label">EMAIL BODY</div>',
        unsafe_allow_html=True
    )

    st.text_area(
        "Body",
        value=st.session_state.body,
        height=300,
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    download_text = (
        f"Subject: {st.session_state.subject}\n\n"
        f"{st.session_state.body}"
    )


    st.download_button(
        "📥 Download Email",
        data=download_text,
        file_name="generated_email.txt",
        mime="text/plain",
        use_container_width=True
    )


    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# HISTORY
# ============================================================

if st.session_state.history:

    st.subheader(
        "Recent Emails"
    )


    for i, item in enumerate(
        st.session_state.history
    ):

        with st.expander(
            f"{i + 1}. {item['subject']}"
        ):

            st.write(
                f"**Language:** {item['language']}"
            )

            st.write(
                f"**Purpose:** {item['purpose']}"
            )

            st.write(
                f"**Recipient:** {item['recipient']}"
            )

            st.write(
                f"**Tone:** {item['tone']}"
            )

            st.write(
                f"**Length:** {item['length']}"
            )

            st.write(
                item["body"]
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    MailMind AI · Powered by Groq · Built with Streamlit
</div>
""", unsafe_allow_html=True)

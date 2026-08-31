// =========================================================
// DOCUMIND AI
// PDF Upload + RAG Chat + New Chat + Midnight/Daylight theme
// =========================================================


// =========================================================
// GET HTML ELEMENTS
// =========================================================

const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const status = document.getElementById("status");

const questionInput = document.getElementById("questionInput");
const chatContainer = document.getElementById("chatContainer");
const askButton = document.getElementById("askButton");

const themeToggle = document.getElementById("themeToggle");
const themeToggleIcon = themeToggle
    ? themeToggle.querySelector(".theme-toggle-icon")
    : null;

const newChatButton = document.getElementById("newChatButton");


// =========================================================
// PDF UPLOAD
// =========================================================

if (uploadForm) {

    uploadForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const file = fileInput.files[0];

        if (!file) {
            setStatus("Choose a PDF first.", true);
            return;
        }

        if (!file.name.toLowerCase().endsWith(".pdf")) {
            setStatus("Only PDF files are supported.", true);
            return;
        }

        const formData = new FormData();

        formData.append("file", file);

        setStatus("Reading the document…", false);

        try {

            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok) {

                const detail = data.chunks
                    ? ` — ${data.pages} page${data.pages === 1 ? "" : "s"}, ${data.chunks} chunks indexed`
                    : "";

                setStatus(`Ready.${detail}`, false);

            } else {

                setStatus(data.error || "Upload failed.", true);

            }

        } catch (error) {

            console.error("Upload error:", error);

            setStatus("Upload failed. Please try again.", true);
        }

    });

}


function setStatus(text, isError) {
    if (!status) {
        return;
    }

    status.textContent = text;
    status.classList.toggle("error", Boolean(isError));
}


// =========================================================
// FILE SELECTION
// =========================================================

if (fileInput) {

    fileInput.addEventListener("change", function () {

        const file = fileInput.files[0];

        if (file) {
            setStatus(`Selected: ${file.name}`, false);
        }

    });

}


// =========================================================
// ASK QUESTION
// =========================================================

async function askQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }


    // Add user question
    addMessage(question, "user-message");


    // Clear input
    questionInput.value = "";


    // Disable button
    if (askButton) {
        askButton.disabled = true;
    }


    // Show loading message
    const loadingMessage = addMessage(
        "Reading the document…",
        "ai-message loading"
    );


    try {

        const response = await fetch(
            "/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        const data = await response.json();


        // Remove loading message
        loadingMessage.remove();


        if (response.ok) {

            addMessage(
                data.answer || "I couldn't generate an answer.",
                "ai-message",
                data.sources
            );

        } else {

            addMessage(
                data.error || "Something went wrong.",
                "ai-message"
            );

        }

    } catch (error) {

        console.error("Question error:", error);

        loadingMessage.remove();

        addMessage(
            "Something went wrong while getting the answer.",
            "ai-message"
        );

    } finally {

        if (askButton) {
            askButton.disabled = false;
        }

        questionInput.focus();
    }

}


// =========================================================
// ASK BUTTON
// =========================================================

if (askButton) {
    askButton.addEventListener("click", askQuestion);
}


// =========================================================
// ADD CHAT MESSAGE
//
// AI answers that cite pages get small mono "page flag" tabs
// (P.2, P.5…) attached to the top edge of the card — like
// sticky tabs left in a real document.
// =========================================================

function addMessage(text, className, sources) {

    const message = document.createElement("div");

    message.className = "message " + className;

    if (Array.isArray(sources) && sources.length > 0) {

        const tabs = document.createElement("div");
        tabs.className = "citation-tabs";

        sources.forEach(function (page) {
            const tab = document.createElement("span");
            tab.className = "citation-tab";
            tab.textContent = `P.${page}`;
            tabs.appendChild(tab);
        });

        message.appendChild(tabs);
    }

    const textNode = document.createElement("span");
    textNode.textContent = text;
    message.appendChild(textNode);

    chatContainer.appendChild(message);

    // Scroll to latest message
    chatContainer.scrollTop = chatContainer.scrollHeight;

    return message;
}


// =========================================================
// ENTER KEY
// =========================================================

if (questionInput) {

    questionInput.addEventListener("keydown", function (event) {

        // Enter = Ask
        // Shift + Enter = New line

        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            askQuestion();
        }

    });

}


// =========================================================
// SUGGESTION BUTTONS
// =========================================================

function askSuggestion(question) {

    if (!questionInput) {
        return;
    }

    questionInput.value = question;
    questionInput.focus();

    askQuestion();
}


// =========================================================
// NEW CHAT
// =========================================================

if (newChatButton) {

    newChatButton.addEventListener("click", function () {

        // Remove previous chat messages only — the Welcome screen
        // already lives in index.html and isn't recreated here.
        if (chatContainer) {

            const messages = chatContainer.querySelectorAll(".message");

            messages.forEach(function (message) {
                message.remove();
            });

        }

        if (questionInput) {
            questionInput.value = "";
        }

        // The document indexed on the server is untouched by "New chat" —
        // this only clears the visible conversation.
        setStatus("", false);

        if (askButton) {
            askButton.disabled = false;
        }

        if (questionInput) {
            questionInput.focus();
        }

    });

}


// =========================================================
// MIDNIGHT / DAYLIGHT THEME
//
// Midnight (dark) is the default desk. Daylight is opt-in and
// saved to localStorage.
// =========================================================

function applyTheme(isLight) {

    document.body.classList.toggle("light-mode", isLight);

    if (themeToggleIcon) {
        // Icon shows the theme you'll switch TO.
        themeToggleIcon.textContent = isLight ? "☾" : "☀";
    }
}

const savedTheme = localStorage.getItem("theme");

applyTheme(savedTheme === "light");

if (themeToggle) {

    themeToggle.addEventListener("click", function () {

        const isLight = !document.body.classList.contains("light-mode");

        applyTheme(isLight);

        localStorage.setItem("theme", isLight ? "light" : "dark");

    });

}


// =========================================================
// INITIAL FOCUS
// =========================================================

if (questionInput) {
    questionInput.focus();
}
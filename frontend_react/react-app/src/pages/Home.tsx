import { useRef, useState } from "react";

interface ChatMessage {
    role: "user" | "bot";
    text: string;
    fileName?: string;
}

interface ChatAttachmentInfo {
    filename: string;
    indexed: boolean;
    chunks_indexed: number;
    note: string | null;
}

interface ChatResponse {
    answer: string;
    citations: string[];
    needs_human_review: boolean;
    model_route: string;
    attachment?: ChatAttachmentInfo;
}

export default function Chat() {

    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    // File states
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileError, setFileError] = useState("");

    // File input reference
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Stable per-tab id sent with every request, so an uploaded file stays
    // searchable for this chat's follow-up questions without leaking to
    // anyone else's session on the shared backend.
    const [sessionId] = useState<string>(() =>
        crypto.randomUUID()
    );


    // ==========================================
    // FILE VALIDATION
    // ==========================================

    const handleFileChange = (
        e: React.ChangeEvent<HTMLInputElement>
    ) => {

        const file = e.target.files?.[0];

        // Clear previous error
        setFileError("");

        if (!file) return;


        // Allowed file types
        const allowedTypes = [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
        ];


        // Maximum file size = 10 MB
        const maxSize = 10 * 1024 * 1024;


        // Validate file type
        if (!allowedTypes.includes(file.type)) {

            setFileError(
                "Only PDF, JPG, PNG and WEBP files are allowed."
            );

            // Reset file input
            e.target.value = "";

            return;
        }


        // Validate file size
        if (file.size > maxSize) {

            setFileError(
                "File size must be less than 10 MB."
            );

            // Reset file input
            e.target.value = "";

            return;
        }


        // File is valid
        setSelectedFile(file);

        console.log("Selected file:", file);
        console.log("File name:", file.name);
        console.log("File type:", file.type);
        console.log("File size:", file.size);
    };


    // ==========================================
    // REMOVE FILE
    // ==========================================

    const removeFile = () => {

        setSelectedFile(null);
        setFileError("");

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };


    // ==========================================
    // SEND MESSAGE
    // ==========================================

    const sendMessage = async () => {

        // Need either typed text or an attached file to send something.
        if (!input.trim() && !selectedFile) return;

        const question =
            input.trim() ||
            "Please analyze the attached file.";

        const userMessage: ChatMessage = {
            role: "user",
            text: question,
            fileName: selectedFile?.name,
        };

        setMessages((prev) => [
            ...prev,
            userMessage,
        ]);

        const fileToSend = selectedFile;

        setInput("");
        removeFile();
        setLoading(true);


        try {

            const formData = new FormData();
            formData.append("question", question);
            formData.append("session_id", sessionId);

            if (fileToSend) {
                formData.append("file", fileToSend);
            }

            const res = await fetch(
                "http://127.0.0.1:8000/chat/",
                {
                    method: "POST",

                    // No Content-Type header here: the browser sets
                    // multipart/form-data with the correct boundary itself.
                    body: formData,
                }
            );


            if (!res.ok) {
                throw new Error(
                    `Server error: ${res.status}`
                );
            }


            const data: ChatResponse =
                await res.json();


            console.log(
                "Chat response:",
                data
            );

            const botMessages: ChatMessage[] = [];

            // Surface an attachment warning (e.g. an image can't be
            // indexed yet, or a scanned PDF had no extractable text).
            if (data.attachment?.note) {
                botMessages.push({
                    role: "bot",
                    text: `⚠️ ${data.attachment.note}`,
                });
            }

            botMessages.push({
                role: "bot",
                text: data.answer,
            });

            setMessages((prev) => [
                ...prev,
                ...botMessages,
            ]);

        } catch (err) {

            console.error(
                "Chat error:",
                err
            );


            setMessages((prev) => [
                ...prev,
                {
                    role: "bot",
                    text: "Sorry, something went wrong.",
                },
            ]);

        } finally {

            setLoading(false);

        }
    };


    // ==========================================
    // ENTER KEY
    // ==========================================

    const handleKeyDown = (
        e: React.KeyboardEvent<HTMLInputElement>
    ) => {

        if (e.key === "Enter") {
            sendMessage();
        }

    };


    // ==========================================
    // UI
    // ==========================================

    return (

        <div
            style={{
                minHeight: "100vh",
                width: "100%",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                backgroundColor: "#d9dbd5",
                fontFamily: "Arial, sans-serif",
            }}
        >

            {/* Main Chat Container */}

            <div
                style={{
                    width: 500,
                    maxWidth: "95%",
                    height: "90vh",
                    display: "flex",
                    flexDirection: "column",
                    backgroundColor: "#efeae2",
                    borderRadius: 10,
                    overflow: "hidden",
                    boxShadow:
                        "0 4px 20px rgba(0, 0, 0, 0.2)",
                }}
            >


                {/* =====================================
                    HEADER
                ===================================== */}

                <div
                    style={{
                        backgroundColor: "#075e54",
                        color: "#ffffff",
                        padding: "14px 24px",
                        display: "flex",
                        alignItems: "center",
                        gap: 16,
                    }}
                >

                    {/* Bot Avatar */}

                    <div
                        style={{
                            width: 58,
                            height: 58,
                            borderRadius: "50%",
                            backgroundColor: "#25d366",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 30,
                            flexShrink: 0,
                        }}
                    >
                        🤖
                    </div>


                    {/* Bot Name */}

                    <div>

                        <div
                            style={{
                                fontSize: 23,
                                fontWeight: "bold",
                            }}
                        >
                            Chatbot
                        </div>


                        <div
                            style={{
                                fontSize: 15,
                                marginTop: 5,
                                opacity: 0.9,
                            }}
                        >
                            {loading
                                ? "typing..."
                                : "online"}
                        </div>

                    </div>

                </div>


                {/* =====================================
                    CHAT AREA
                ===================================== */}

                <div
                    style={{
                        flex: 1,
                        padding: 16,
                        overflowY: "auto",
                        display: "flex",
                        flexDirection: "column",
                        gap: 8,
                        backgroundColor: "#efeae2",
                    }}
                >

                    {/* Empty Chat Message */}

                    {messages.length === 0 && (

                        <div
                            style={{
                                color: "#54656f",
                                textAlign: "center",
                                marginTop: 220,
                                fontSize: 16,
                            }}
                        >
                            🔒 How can I assist you today !!
                            <br />
                            <br />
                            Start the conversation...
                        </div>

                    )}


                    {/* Messages */}

                    {messages.map((msg, i) => (

                        <div
                            key={i}
                            style={{
                                alignSelf:
                                    msg.role === "user"
                                        ? "flex-end"
                                        : "flex-start",

                                backgroundColor:
                                    msg.role === "user"
                                        ? "#d9fdd3"
                                        : "#ffffff",

                                color: "#111b21",

                                padding: "9px 13px",

                                borderRadius:
                                    msg.role === "user"
                                        ? "8px 0px 8px 8px"
                                        : "0px 8px 8px 8px",

                                maxWidth: "75%",

                                fontSize: 14,

                                lineHeight: 1.5,

                                boxShadow:
                                    "0 1px 1px rgba(0, 0, 0, 0.1)",

                                wordBreak: "break-word",
                            }}
                        >
                            {msg.fileName && (
                                <div
                                    style={{
                                        fontSize: 12,
                                        opacity: 0.7,
                                        marginBottom: 4,
                                    }}
                                >
                                    📎 {msg.fileName}
                                </div>
                            )}
                            {msg.text}
                        </div>

                    ))}


                    {/* Typing Indicator */}

                    {loading && (

                        <div
                            style={{
                                alignSelf: "flex-start",
                                backgroundColor: "#ffffff",
                                color: "#667781",
                                padding: "9px 13px",
                                borderRadius:
                                    "0px 8px 8px 8px",
                                fontSize: 14,
                                boxShadow:
                                    "0 1px 1px rgba(0, 0, 0, 0.1)",
                            }}
                        >
                            typing...
                        </div>

                    )}

                </div>


                {/* =====================================
                    FILE ERROR
                ===================================== */}

                {fileError && (

                    <div
                        style={{
                            backgroundColor: "#f0f2f5",
                            color: "#d32f2f",
                            padding: "6px 14px",
                            fontSize: 12,
                        }}
                    >
                        ⚠️ {fileError}
                    </div>

                )}


                {/* =====================================
                    SELECTED FILE
                ===================================== */}

                {selectedFile && (

                    <div
                        style={{
                            backgroundColor: "#f0f2f5",
                            padding: "8px 14px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            borderTop:
                                "1px solid #ddd",
                        }}
                    >

                        <span
                            style={{
                                fontSize: 13,
                                color: "#111b21",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                whiteSpace: "nowrap",
                                maxWidth: "85%",
                            }}
                        >

                            {selectedFile.type ===
                            "application/pdf"
                                ? "📄"
                                : "🖼️"}

                            {" "}

                            {selectedFile.name}

                        </span>


                        <button
                            type="button"
                            onClick={removeFile}
                            style={{
                                border: "none",
                                backgroundColor:
                                    "transparent",
                                cursor: "pointer",
                                fontSize: 14,
                            }}
                        >
                            ❌
                        </button>

                    </div>

                )}


                {/* =====================================
                    INPUT AREA
                ===================================== */}

                <div
                    style={{
                        backgroundColor: "#f0f2f5",
                        padding: "12px 14px",
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                    }}
                >

                    {/* =================================
                        ATTACH BUTTON
                    ================================= */}

                    <button
                        type="button"
                        onClick={() =>
                            fileInputRef.current?.click()
                        }
                        style={{
                            width: 42,
                            height: 42,
                            borderRadius: "50%",
                            border: "none",
                            backgroundColor:
                                "transparent",
                            cursor: "pointer",
                            fontSize: 22,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                        }}
                    >
                        📎
                    </button>


                    {/* Hidden File Input */}

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png,.webp"
                        onChange={handleFileChange}
                        hidden
                    />


                    {/* =================================
                        MESSAGE INPUT
                    ================================= */}

                    <input
                        type="text"
                        value={input}
                        onChange={(e) =>
                            setInput(e.target.value)
                        }
                        onKeyDown={handleKeyDown}
                        placeholder="Type a message"
                        style={{
                            flex: 1,
                            padding:
                                "13px 18px",
                            borderRadius: 24,
                            border: "none",
                            outline: "none",
                            fontSize: 15,
                            color: "#111b21",
                            backgroundColor:
                                "#ffffff",
                        }}
                    />


                    {/* =================================
                        SEND BUTTON
                    ================================= */}

                    <button
                        onClick={sendMessage}
                        disabled={loading}
                        style={{
                            width: 48,
                            height: 48,
                            borderRadius: "50%",
                            border: "none",

                            backgroundColor:
                                loading
                                    ? "#8696a0"
                                    : "#25d366",

                            color: "#ffffff",

                            cursor:
                                loading
                                    ? "not-allowed"
                                    : "pointer",

                            fontSize: 21,

                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",

                            flexShrink: 0,
                        }}
                    >
                        ➤
                    </button>

                </div>

            </div>

        </div>

    );
}  
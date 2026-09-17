import { useState } from "react"


interface ChatMessage {
    role : "user" | "bot"
    text : string

}

interface ChatResponse {
    answer : string
    model_routing : string
    input_tokens : number
    output_tokens : number
    estimated_cost_usd : number
    needs_human_review : boolean
}

export default function Chat() {
    const [messages , setMessages] = useState<ChatMessage[]>([])
    const [input, setInput] = useState("")
    const [loading , setLoading] = useState(false)


    const sendMessage = async () => {
        if (!input.trim()) return 

        const userMessage : ChatMessage = {role : "user", text : input}
        setMessages((prev) => [...prev, userMessage])
        setInput("")
        setLoading(true)

        try {
            const res = await fetch("http://127.0.0.1:8000/chat", {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    message : input,
                })

            })

            if (!res.ok){
                throw new Error(`Server error : ${res.status}`)
            }
            
            const data : ChatResponse = await res.json()

            const botMessage : ChatMessage = {
                role : "bot",
                text : data.answer,

            }

            setMessages((prev) => [...prev, botMessage])
        } catch(err){
            console.error("Chat error :",err)

            setMessages((prev) => [
                ...prev,
                {
                 role : "bot",
                 text : "Sorry, something went wrong.", 
                },
            ])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e : React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter"){
            sendMessage()
        }
    }
   


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
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
        }}
      >
        {/* Header */}
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
              {loading ? "typing..." : "online"}
            </div>
          </div>
        </div>

        {/* Chat Area */}
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
              🔒 How can i assist you today !!
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
                  msg.role === "user" ? "flex-end" : "flex-start",

                backgroundColor:
                  msg.role === "user" ? "#d9fdd3" : "#ffffff",

                color: "#111b21",

                padding: "9px 13px",

                borderRadius:
                  msg.role === "user"
                    ? "8px 0px 8px 8px"
                    : "0px 8px 8px 8px",

                maxWidth: "75%",

                fontSize: 14,

                lineHeight: 1.5,

                boxShadow: "0 1px 1px rgba(0, 0, 0, 0.1)",

                wordBreak: "break-word",
              }}
            >
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
                borderRadius: "0px 8px 8px 8px",
                fontSize: 14,
                boxShadow: "0 1px 1px rgba(0, 0, 0, 0.1)",
              }}
            >
              typing...
            </div>
          )}
        </div>

        {/* Input Area */}
        <div
          style={{
            backgroundColor: "#f0f2f5",
            padding: "12px 14px",
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message"
            style={{
              flex: 1,
              padding: "13px 18px",
              borderRadius: 24,
              border: "none",
              outline: "none",
              fontSize: 15,

              // Important: makes typed text visible
              color: "#111b21",

              backgroundColor: "#ffffff",
            }}
          />

          {/* Send Button */}
          <button
            onClick={sendMessage}
            disabled={loading}
            style={{
              width: 48,
              height: 48,
              borderRadius: "50%",
              border: "none",
              backgroundColor: loading ? "#8696a0" : "#25d366",
              color: "#ffffff",
              cursor: loading ? "not-allowed" : "pointer",
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
  )
}
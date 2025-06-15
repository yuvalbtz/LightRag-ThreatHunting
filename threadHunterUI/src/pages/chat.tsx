import { useState, useRef, useEffect } from "react";
import { Card, CardBody as CardContent, CardFooter } from "@heroui/card";
import { Button } from "@heroui/button";
import { Textarea } from "@heroui/input";
import { PaperAirplaneIcon } from "@heroicons/react/24/solid"; // Use Heroicons

type Message = {
    role: "user" | "assistant";
    content: string;
};

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMsg: Message = { role: "user", content: input };
        setMessages((msgs) => [...msgs, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                body: JSON.stringify({ message: input }),
                headers: { "Content-Type": "application/json" },
            });
            const data = await response.json();
            setMessages((msgs) => [
                ...msgs,
                { role: "assistant", content: data.reply || "No response." },
            ]);
        } catch (e) {
            setMessages((msgs) => [
                ...msgs,
                { role: "assistant", content: "Error contacting server." },
            ]);
        }
        setLoading(false);
    };

    return (
        <div className="fixed inset-0 bg-background flex flex-col items-center justify-center">
            <div className="w-full max-w-3xl flex flex-col flex-1 bg-white/80 border rounded-lg shadow-lg overflow-hidden my-4">
                {/* Chat Messages */}
                <div className="flex-1 overflow-y-auto px-4 py-6 bg-background">
                    {messages.length === 0 && (
                        <div className="text-center text-gray-400 mt-20">
                            Start the conversation!
                        </div>
                    )}
                    <div className="flex flex-col gap-4">
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                                <div
                                    className={`p-3 rounded-xl max-w-[75%] break-words shadow ${msg.role === "user"
                                        ? "bg-blue-600 text-white"
                                        : "bg-gray-100 text-gray-900"
                                        }`}
                                >
                                    {msg.content}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </div>
                {/* Input */}
                <div className="w-full border-t bg-background px-4 py-4">
                    <form
                        className="flex gap-2"
                        onSubmit={(e) => {
                            e.preventDefault();
                            sendMessage();
                        }}
                    >
                        <Textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message..."
                            className="flex-1 resize-none"
                            rows={1}
                            minRows={1}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey) {
                                    e.preventDefault();
                                    sendMessage();
                                }
                            }}
                            disabled={loading}
                        />
                        <Button type="submit" disabled={loading || !input.trim()} aria-label="Send">
                            {loading ? "Sending..." : <PaperAirplaneIcon className="w-5 h-5" />}
                        </Button>
                    </form>
                </div>
            </div>
        </div>
    );
}